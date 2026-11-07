package kr.palcheonjo.alarm1560;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.*;
import android.os.*;

/** Playback always uses the OS ALARM stream, never STREAM_MUSIC. */
public final class AlarmAudio {
  private static final java.util.concurrent.ExecutorService RELEASER =
      java.util.concurrent.Executors.newSingleThreadExecutor(
          r -> {
            Thread t = new Thread(r, "alarm-audio-release");
            t.setDaemon(true);
            return t;
          });

  private static void release(MediaPlayer p) {
    RELEASER.execute(p::release);
  }

  private final Context context;
  private final Handler handler = new Handler(Looper.getMainLooper());
  private MediaPlayer player;
  private AudioFocusRequest focus;
  private Vibrator vibrator;
  private boolean stopped = true;
  private long began;
  private Alarm alarm;
  private AudioAttributes attributes;
  private final Runnable ramp =
      new Runnable() {
        @Override
        public void run() {
          if (stopped || player == null) return;
          float gain = alarm.volume / 100f;
          if (alarm.ramp)
            gain *= Math.min(1f, .10f + (SystemClock.elapsedRealtime() - began) / 30000f * .90f);
          try {
            player.setVolume(gain, gain);
          } catch (IllegalStateException ignored) {
          }
          if (alarm.ramp && SystemClock.elapsedRealtime() - began < 30000)
            handler.postDelayed(this, 250);
        }
      };

  public AlarmAudio(Context c) {
    context = c.getApplicationContext();
  }

  public void start(Alarm a, boolean vibrate) {
    stop();
    alarm = a;
    stopped = false;
    attributes =
        new AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_ALARM)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build();
    AudioManager am = context.getSystemService(AudioManager.class);
    focus =
        new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
            .setAudioAttributes(attributes)
            .setOnAudioFocusChangeListener(
                change -> {
                  if (player == null || stopped) return;
                  if (change == AudioManager.AUDIOFOCUS_LOSS) {
                    stop();
                    Engine.log(context, "다른 앱이 소리를 사용해 재생이 중단되었습니다");
                  } else if (change == AudioManager.AUDIOFOCUS_LOSS_TRANSIENT) {
                    try {
                      player.pause();
                    } catch (IllegalStateException ignored) {
                    }
                  } else if (change == AudioManager.AUDIOFOCUS_GAIN) {
                    try {
                      player.start();
                    } catch (IllegalStateException ignored) {
                    }
                  }
                },
                handler)
            .build();
    if (am.requestAudioFocus(focus) != AudioManager.AUDIOFOCUS_REQUEST_GRANTED)
      Engine.log(context, "알람 오디오 사용 권한이 거절되었습니다");
    prepare(0);
    if (vibrate && a.vibrate) {
      vibrator = context.getSystemService(Vibrator.class);
      if (vibrator != null && vibrator.hasVibrator())
        vibrator.vibrate(
            VibrationEffect.createWaveform(new long[] {0, 600, 400, 600, 1000}, 0), attributes);
    }
  }

  /** Never block the activity/service main thread while a decoder or audio HAL starts. */
  private void prepare(int attempt) {
    if (stopped) return;
    handler.removeCallbacks(ramp);
    MediaPlayer current = new MediaPlayer();
    player = current;
    current.setAudioAttributes(attributes);
    current.setOnPreparedListener(
        p -> {
          if (stopped || player != p) return;
          try {
            began = SystemClock.elapsedRealtime();
            p.setLooping(true);
            ramp.run();
            p.start();
          } catch (IllegalStateException error) {
            failed(p, attempt);
          }
        });
    current.setOnErrorListener(
        (p, what, extra) -> {
          failed(p, attempt);
          return true;
        });
    try {
      if (attempt < 2) {
        String file = attempt == 0 ? Sounds.file(alarm.sound) : Sounds.file("bell");
        try (AssetFileDescriptor fd = context.getAssets().openFd(file)) {
          current.setDataSource(fd.getFileDescriptor(), fd.getStartOffset(), fd.getLength());
        }
      } else
        current.setDataSource(context, android.provider.Settings.System.DEFAULT_ALARM_ALERT_URI);
      current.prepareAsync();
    } catch (Exception error) {
      failed(current, attempt);
    }
  }

  private void failed(MediaPlayer p, int attempt) {
    if (player != p || stopped) return;
    release(p);
    player = null;
    if (attempt < 2) {
      Engine.log(context, "선택한 소리 재생 실패 · 기본 알람음으로 재생");
      prepare(attempt + 1);
    } else Engine.log(context, "알람 소리 오류 · 소리 미리듣기로 확인해 주세요");
  }

  public void stop() {
    stopped = true;
    handler.removeCallbacksAndMessages(null);
    if (player != null) {
      MediaPlayer previous = player;
      player = null;
      release(previous);
    }
    if (vibrator != null) {
      vibrator.cancel();
      vibrator = null;
    }
    if (focus != null) {
      context.getSystemService(AudioManager.class).abandonAudioFocusRequest(focus);
      focus = null;
    }
  }
}
