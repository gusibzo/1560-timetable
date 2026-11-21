package kr.palcheonjo.routevideo1560;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Rect;
import android.graphics.Typeface;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.ResultReceiver;
import android.os.SystemClock;
import android.util.DisplayMetrics;
import android.view.WindowInsets;
import android.view.WindowManager;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.EnumMap;
import java.util.Locale;

public final class RouteVideoActivity extends Activity {
  private enum Route {
    A("2NzYyMzQwMDA4ODQ0NDkw4"),
    B("5NDYzMjMyMjgwMDA0MzM2MDUzNg5");

    final String number = "1560" + name();
    final String url;

    Route(String path) {
      url = "https://m.gbis.go.kr/routeBusLocation/" + path;
    }
  }

  private static final int CAPTURE_REQUEST = 156;
  private static final int NAVY = Color.rgb(23, 55, 90);
  private static final DateTimeFormatter CLOCK_FORMAT =
      DateTimeFormatter.ofPattern("uuuu-MM-dd (EEE) HH:mm:ss", Locale.KOREA);
  private final Handler handler = new Handler(Looper.getMainLooper());
  private final EnumMap<Route, Uri> latestVideos = new EnumMap<>(Route.class);
  private WebView web;
  private TextView clock;
  private TextView status;
  private Button routeA;
  private Button routeB;
  private Button capture;
  private Button play;
  private String scrollScript;
  private Route route;
  private boolean autoRequest;
  private boolean ready;
  private boolean loading;
  private boolean asking;
  private boolean starting;
  private boolean recording;
  private boolean stopping;
  private boolean routeInterrupted;
  private long loadDeadline;
  private int loadGeneration;
  private Intent captureGrant;
  private int captureResult;

  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    Route requested = routeFromTimetable(getIntent());
    autoRequest = state == null && requested != null;
    route = state != null ? Route.valueOf(state.getString("route", "B"))
        : requested != null ? requested : Route.B;
    try {
      scrollScript = loadScrollScript();
    } catch (IOException error) {
      Toast.makeText(this, "자동 스크롤을 준비할 수 없습니다.", Toast.LENGTH_LONG).show();
      finish();
      return;
    }
    createScreen();
    loadRoute();
  }

  @Override protected void onNewIntent(Intent intent) {
    super.onNewIntent(intent);
    setIntent(intent);
    Route requested = routeFromTimetable(intent);
    if (requested != null && !busy()) {
      autoRequest = true;
      if (requested != route || (!ready && !loading)) {
        route = requested;
        loadRoute();
      } else {
        maybeRequest();
      }
    }
  }

  private Route routeFromTimetable(Intent intent) {
    Uri link = intent.getData();
    if (!Intent.ACTION_VIEW.equals(intent.getAction()) || link == null
        || !"routevideo1560ab".equals(link.getScheme()) || !"record".equals(link.getHost())) return null;
    if ("/A".equals(link.getPath())) return Route.A;
    if ("/B".equals(link.getPath())) return Route.B;
    return null;
  }

  @Override protected void onSaveInstanceState(Bundle state) {
    state.putString("route", route.name());
    super.onSaveInstanceState(state);
  }

  private String loadScrollScript() throws IOException {
    try (InputStream stream = getAssets().open("route-scroll.js");
         ByteArrayOutputStream result = new ByteArrayOutputStream()) {
      byte[] buffer = new byte[4096];
      int length;
      while ((length = stream.read(buffer)) != -1) result.write(buffer, 0, length);
      return new String(result.toByteArray(), StandardCharsets.UTF_8);
    }
  }

  private int dp(int value) {
    return Math.round(value * getResources().getDisplayMetrics().density);
  }

  private void createScreen() {
    LinearLayout root = new LinearLayout(this);
    root.setOrientation(LinearLayout.VERTICAL);
    root.setBackgroundColor(Color.WHITE);
    if (Build.VERSION.SDK_INT >= 30) {
      root.setOnApplyWindowInsetsListener((view, insets) -> {
        android.graphics.Insets bars = insets.getInsets(
            WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
        root.setPadding(bars.left, bars.top, bars.right, bars.bottom);
        return insets;
      });
      getWindow().getDecorView().setSystemUiVisibility(
          android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
              | android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
      getWindow().setDecorFitsSystemWindows(false);
    }

    // The clock belongs to the app surface, so single-app capture includes it.
    clock = new TextView(this);
    clock.setTextSize(17);
    clock.setTextColor(Color.WHITE);
    clock.setBackgroundColor(NAVY);
    clock.setTypeface(Typeface.MONOSPACE, Typeface.BOLD);
    clock.setGravity(android.view.Gravity.CENTER);
    clock.setPadding(dp(6), dp(8), dp(6), dp(8));
    root.addView(clock, new LinearLayout.LayoutParams(-1, -2));

    LinearLayout routePicker = new LinearLayout(this);
    routePicker.setPadding(dp(8), 0, dp(8), 0);
    routeA = addRouteButton(routePicker, Route.A);
    routeB = addRouteButton(routePicker, Route.B);
    root.addView(routePicker, new LinearLayout.LayoutParams(-1, -2));

    LinearLayout toolbar = new LinearLayout(this);
    toolbar.setGravity(android.view.Gravity.CENTER_VERTICAL);
    toolbar.setPadding(dp(12), dp(4), dp(8), dp(4));
    status = new TextView(this);
    status.setTextSize(14);
    status.setTextColor(Color.rgb(23, 37, 63));
    status.setAccessibilityLiveRegion(android.view.View.ACCESSIBILITY_LIVE_REGION_POLITE);
    toolbar.addView(status, new LinearLayout.LayoutParams(0, -2, 1));
    play = new Button(this);
    play.setText("영상 보기");
    play.setVisibility(android.view.View.GONE);
    play.setOnClickListener(view -> playMovie());
    toolbar.addView(play, new LinearLayout.LayoutParams(-2, -2));
    capture = new Button(this);
    capture.setOnClickListener(view -> {
      if (recording) stopCapture();
      else if (ready) requestCapture();
      else if (!loading) loadRoute();
    });
    toolbar.addView(capture, new LinearLayout.LayoutParams(-2, -2));
    root.addView(toolbar, new LinearLayout.LayoutParams(-1, -2));

    web = new WebView(this);
    WebSettings settings = web.getSettings();
    settings.setJavaScriptEnabled(true);
    settings.setDomStorageEnabled(true);
    settings.setAllowFileAccess(false);
    settings.setAllowContentAccess(false);
    settings.setGeolocationEnabled(false);
    settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    web.setOnTouchListener((view, event) -> busy());
    web.setWebViewClient(new WebViewClient() {
      @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
        return request.isForMainFrame() && !route.url.equals(request.getUrl().toString());
      }

      @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
        if (request.isForMainFrame() && loading && route.url.equals(request.getUrl().toString())) loadFailed();
      }

      @Override public void onPageFinished(WebView view, String url) {
        if (loading && route.url.equals(url)) checkRoute(loadGeneration);
      }
    });
    root.addView(web, new LinearLayout.LayoutParams(-1, 0, 1));
    setContentView(root);
  }

  private final Runnable updateClock = new Runnable() {
    @Override public void run() {
      if (clock == null) return;
      clock.setText(CLOCK_FORMAT.format(ZonedDateTime.now()));
      handler.postDelayed(this, 1_000 - System.currentTimeMillis() % 1_000);
    }
  };

  private Button addRouteButton(LinearLayout picker, Route choice) {
    Button button = new Button(this);
    button.setText(choice.number);
    button.setOnClickListener(view -> {
      if (route == choice || busy()) return;
      autoRequest = false;
      route = choice;
      loadRoute();
    });
    picker.addView(button, new LinearLayout.LayoutParams(0, -2, 1));
    return button;
  }

  private void loadRoute() {
    autoRequest = autoRequest && !busy();
    ready = false;
    loading = true;
    loadGeneration++;
    loadDeadline = SystemClock.uptimeMillis() + 25_000;
    update(route.number + " 실시간 위치 불러오는 중");
    web.loadUrl(route.url);
    handler.removeCallbacks(loadTimeout);
    handler.postDelayed(loadTimeout, 25_000);
  }

  private final Runnable loadTimeout = () -> {
    if (loading) loadFailed();
  };

  private String scrollCall(String method) {
    return "window.routeVideo1560?." + method + "('" + route.name() + "')";
  }

  private void checkRoute(int generation) {
    if (generation != loadGeneration || !loading || isDestroyed()) return;
    web.evaluateJavascript(scrollScript + "\n" + scrollCall("ready"), result -> {
      if (generation != loadGeneration || !loading || isDestroyed()) return;
      if ("true".equals(result)) {
        ready = true;
        loading = false;
        handler.removeCallbacks(loadTimeout);
        update(route.number + " 실시간 버스 위치");
        maybeRequest();
      } else if (SystemClock.uptimeMillis() < loadDeadline) {
        handler.postDelayed(() -> checkRoute(generation), 300);
      } else {
        loadFailed();
      }
    });
  }

  private void loadFailed() {
    loading = false;
    autoRequest = false;
    handler.removeCallbacks(loadTimeout);
    update("노선을 불러오지 못했습니다.");
  }

  private boolean busy() {
    return asking || starting || recording || stopping;
  }

  private void update(String message) {
    status.setText(message);
    updateRouteButton(routeA, route == Route.A);
    updateRouteButton(routeB, route == Route.B);
    capture.setText(recording ? "녹화 끝내기" : ready ? "녹화 시작" : "다시 불러오기");
    capture.setEnabled(recording || (!busy() && !loading));
    play.setVisibility(latestVideos.containsKey(route) && !busy()
        ? android.view.View.VISIBLE : android.view.View.GONE);
  }

  private void updateRouteButton(Button button, boolean selected) {
    button.setSelected(selected);
    button.setEnabled(!busy());
    button.setBackgroundTintList(ColorStateList.valueOf(selected ? NAVY : Color.rgb(231, 238, 247)));
    button.setTextColor(selected ? Color.WHITE : NAVY);
  }

  private void maybeRequest() {
    if (autoRequest && ready && !busy() && hasWindowFocus() && !isFinishing()) requestCapture();
  }

  private void requestCapture() {
    autoRequest = false;
    asking = true;
    routeInterrupted = false;
    update("화면 공유 권한을 확인해 주세요.");
    MediaProjectionManager manager = getSystemService(MediaProjectionManager.class);
    try {
      startActivityForResult(manager.createScreenCaptureIntent(), CAPTURE_REQUEST);
    } catch (RuntimeException error) {
      asking = false;
      update("화면 녹화 권한을 열 수 없습니다.");
    }
  }

  @Override protected void onActivityResult(int request, int result, Intent data) {
    super.onActivityResult(request, result, data);
    if (request != CAPTURE_REQUEST) return;
    asking = false;
    if (result != RESULT_OK || data == null) {
      update("화면 공유가 취소되었습니다.");
      return;
    }
    captureGrant = data;
    captureResult = result;
    starting = true;
    update("노선의 맨 위로 이동 중");
    startWhenVisible();
  }

  @Override public void onWindowFocusChanged(boolean focused) {
    super.onWindowFocusChanged(focused);
    if (focused) {
      startWhenVisible();
      maybeRequest();
    } else if (recording) {
      stopCapture();
    }
  }

  private void startWhenVisible() {
    if (captureGrant == null || !hasWindowFocus() || isFinishing()) return;
    Intent grant = captureGrant;
    captureGrant = null;
    web.evaluateJavascript(scrollCall("rewind"), result -> {
      if (!starting || isFinishing() || isDestroyed()) return;
      if (!"true".equals(result) || !hasWindowFocus()) {
        starting = false;
        update("노선 화면을 열고 다시 녹화해 주세요.");
        return;
      }

      int[] size = videoSize();
      Intent service = new Intent(this, RecordingService.class)
          .putExtra("grant", grant)
          .putExtra("resultCode", captureResult)
          .putExtra("receiver", receiver)
          .putExtra("route", route.number)
          .putExtra("width", size[0])
          .putExtra("height", size[1]);
      try {
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        startForegroundService(service);
      } catch (RuntimeException error) {
        starting = false;
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        update("녹화를 시작할 수 없습니다.");
      }
    });
  }

  private int[] videoSize() {
    DisplayMetrics metrics = getResources().getDisplayMetrics();
    int width = metrics.widthPixels;
    int height = metrics.heightPixels;
    if (Build.VERSION.SDK_INT >= 30) {
      Rect bounds = getWindowManager().getMaximumWindowMetrics().getBounds();
      width = bounds.width();
      height = bounds.height();
    }
    double scale = Math.min(1.0, Math.min(720.0 / width, 1800.0 / height));
    return new int[]{(int) (width * scale) / 2 * 2, (int) (height * scale) / 2 * 2};
  }

  private final ResultReceiver receiver = new ResultReceiver(handler) {
    @Override protected void onReceiveResult(int code, Bundle data) {
      if (isFinishing() || isDestroyed()) {
        stopService(new Intent(RouteVideoActivity.this, RecordingService.class));
        return;
      }
      if (code == RecordingService.STARTED) {
        if (!starting || !hasWindowFocus()) {
          stopCapture();
          return;
        }
        starting = false;
        recording = true;
        update("● " + route.number + " 녹화 중");
        web.evaluateJavascript(scrollCall("start"), result -> {
          if (!recording) return;
          if ("true".equals(result)) monitorScroll();
          else interruptRoute();
        });
      } else {
        starting = recording = stopping = false;
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        web.evaluateJavascript("window.routeVideo1560?.stop()", null);
        if (code == RecordingService.SAVED) {
          latestVideos.put(route, Uri.parse(data.getString("uri")));
          update(routeInterrupted ? "중단 지점까지 저장했습니다." : "갤러리에 영상을 저장했습니다.");
        } else {
          update("녹화 영상을 저장하지 못했습니다.");
        }
      }
    }
  };

  private void monitorScroll() {
    if (!recording) return;
    web.evaluateJavascript("window.routeVideo1560?.state()", result -> {
      if (!recording) return;
      if ("\"done\"".equals(result)) stopCapture();
      else if ("\"running\"".equals(result)) handler.postDelayed(this::monitorScroll, 300);
      else interruptRoute();
    });
  }

  private void interruptRoute() {
    routeInterrupted = true;
    stopCapture();
  }

  private void stopCapture() {
    captureGrant = null;
    starting = recording = false;
    stopping = true;
    web.evaluateJavascript("window.routeVideo1560?.stop()", null);
    update("영상 저장 중");
    if (!stopService(new Intent(this, RecordingService.class))) {
      stopping = false;
      getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
      update("녹화할 화면을 준비하지 못했습니다.");
    }
  }

  private void playMovie() {
    try {
      startActivity(new Intent(Intent.ACTION_VIEW).setDataAndType(latestVideos.get(route), "video/mp4")
          .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION));
    } catch (ActivityNotFoundException error) {
      Toast.makeText(this, "갤러리의 1560 폴더에서 열 수 있습니다.", Toast.LENGTH_LONG).show();
    }
  }

  @Override protected void onStart() {
    super.onStart();
    updateClock.run();
  }

  @Override protected void onStop() {
    handler.removeCallbacks(updateClock);
    if (!asking && (recording || starting)) stopCapture();
    super.onStop();
  }

  @Override protected void onDestroy() {
    handler.removeCallbacksAndMessages(null);
    if (web != null) web.destroy();
    super.onDestroy();
  }
}
