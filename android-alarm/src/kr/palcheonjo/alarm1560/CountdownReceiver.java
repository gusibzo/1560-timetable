package kr.palcheonjo.alarm1560;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

public final class CountdownReceiver extends BroadcastReceiver {
  @Override
  public void onReceive(Context context, Intent intent) {
    if (!"TIMER_DUE".equals(intent.getAction())) return;
    try {
      new CountdownTimers(context).finishDue();
    } catch (RuntimeException error) {
      Log.w("Alarm1560", "Could not record timer completion", error);
    }
  }
}
