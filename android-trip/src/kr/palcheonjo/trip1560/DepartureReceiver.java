package kr.palcheonjo.trip1560;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public final class DepartureReceiver extends BroadcastReceiver {
  @Override public void onReceive(Context context, Intent intent) {
    long at = intent.getLongExtra("at", 0);
    if (at <= 0 || at != TripService.state(context).getLong("at", 0)) return;
    context.startForegroundService(new Intent(context, TripService.class).setAction(TripService.DUE));
  }
}
