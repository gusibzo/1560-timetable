package kr.palcheonjo.routevideo1560;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.MediaRecorder;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.ParcelFileDescriptor;
import android.os.ResultReceiver;
import android.provider.MediaStore;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public final class RecordingService extends Service {
  static final int STARTED = 1;
  static final int SAVED = 2;
  static final int FAILED = 3;
  private static final String CHANNEL = "route_video";
  private final Handler handler = new Handler(Looper.getMainLooper());
  private final MediaProjection.Callback projectionCallback = new MediaProjection.Callback() {
    @Override public void onStop() { finishCapture(); }
  };
  private MediaProjection projection;
  private VirtualDisplay display;
  private MediaRecorder recorder;
  private ParcelFileDescriptor file;
  private Uri output;
  private ResultReceiver receiver;
  private boolean started;
  private boolean finished;

  @Override public IBinder onBind(Intent intent) { return null; }

  @Override public int onStartCommand(Intent intent, int flags, int startId) {
    if (intent == null || "stop".equals(intent.getAction())) {
      finishCapture();
      return START_NOT_STICKY;
    }
    if (receiver != null) return START_NOT_STICKY;

    receiver = intent.getParcelableExtra("receiver");
    String route = "1560A".equals(intent.getStringExtra("route")) ? "1560A" : "1560B";
    try {
      startForeground(1560, notification(route), ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
      MediaProjectionManager manager = getSystemService(MediaProjectionManager.class);
      Intent grant = intent.getParcelableExtra("grant");
      projection = manager.getMediaProjection(intent.getIntExtra("resultCode", 0), grant);
      if (projection == null) throw new IOException("No projection grant");
      projection.registerCallback(projectionCallback, handler);
      int width = intent.getIntExtra("width", 720);
      int height = intent.getIntExtra("height", 1560);
      prepareRecorder(route, width, height);
      display = projection.createVirtualDisplay(route, width, height, getResources().getDisplayMetrics().densityDpi,
          DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, recorder.getSurface(), null, handler);
      if (display == null) throw new IOException("No virtual display");
      recorder.start();
      started = true;
      handler.postDelayed(this::finishCapture, 120_000);
      send(STARTED, null);
    } catch (IOException | RuntimeException error) {
      finishCapture();
    }
    return START_NOT_STICKY;
  }

  private Notification notification(String route) {
    NotificationManager manager = getSystemService(NotificationManager.class);
    manager.createNotificationChannel(new NotificationChannel(
        CHANNEL, "1560 A·B 노선 녹화", NotificationManager.IMPORTANCE_LOW));
    PendingIntent stop = PendingIntent.getService(this, 0,
        new Intent(this, RecordingService.class).setAction("stop"),
        PendingIntent.FLAG_IMMUTABLE);
    return new Notification.Builder(this, CHANNEL)
        .setSmallIcon(android.R.drawable.presence_video_online)
        .setContentTitle(route + " 노선 화면 녹화 중")
        .setOngoing(true)
        .addAction(new Notification.Action.Builder(null, "녹화 끝내기", stop).build())
        .build();
  }

  private void prepareRecorder(String route, int width, int height) throws IOException {
    String time = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.ROOT).format(new Date());
    ContentValues values = new ContentValues();
    values.put(MediaStore.Video.Media.DISPLAY_NAME, route + "_" + time + ".mp4");
    values.put(MediaStore.Video.Media.MIME_TYPE, "video/mp4");
    values.put(MediaStore.Video.Media.RELATIVE_PATH, Environment.DIRECTORY_MOVIES + "/1560");
    values.put(MediaStore.Video.Media.IS_PENDING, 1);
    output = getContentResolver().insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values);
    if (output == null) throw new IOException("Could not create movie");
    file = getContentResolver().openFileDescriptor(output, "rw");
    if (file == null) throw new IOException("Could not open movie");

    recorder = Build.VERSION.SDK_INT >= 31 ? new MediaRecorder(this) : new MediaRecorder();
    recorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
    recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
    recorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
    recorder.setVideoSize(width, height);
    recorder.setVideoFrameRate(30);
    recorder.setVideoEncodingBitRate(3_000_000);
    recorder.setOutputFile(file.getFileDescriptor());
    recorder.setOnErrorListener((source, what, extra) -> finishCapture());
    recorder.prepare();
  }

  private void send(int code, Uri uri) {
    if (receiver == null) return;
    Bundle data = new Bundle();
    if (uri != null) data.putString("uri", uri.toString());
    receiver.send(code, data);
  }

  private void finishCapture() {
    if (finished) return;
    finished = true;
    handler.removeCallbacksAndMessages(null);
    boolean saved = false;
    if (started) {
      try {
        recorder.stop();
        saved = true;
      } catch (RuntimeException ignored) {
        // Very short or interrupted captures may contain no output frames.
      }
    }
    if (display != null) display.release();
    if (recorder != null) recorder.release();
    if (projection != null) {
      projection.unregisterCallback(projectionCallback);
      projection.stop();
    }
    if (file != null) {
      try { file.close(); } catch (IOException ignored) { saved = false; }
    }
    if (output != null) {
      try {
        if (saved) {
          ContentValues values = new ContentValues();
          values.put(MediaStore.Video.Media.IS_PENDING, 0);
          saved = getContentResolver().update(output, values, null, null) == 1;
        }
        if (!saved) getContentResolver().delete(output, null, null);
      } catch (RuntimeException error) {
        saved = false;
      }
    }
    send(saved ? SAVED : FAILED, saved ? output : null);
    stopForeground(STOP_FOREGROUND_REMOVE);
    stopSelf();
  }

  @Override public void onDestroy() {
    finishCapture();
    super.onDestroy();
  }
}
