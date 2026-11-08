package kr.palcheonjo.alarm1560;

import android.content.Context;
import android.graphics.*;
import android.view.View;

/** Small native vector glyphs that stay crisp at the phone's text/display size. */
final class AlarmArt extends View {
  private final String kind;
  private int tint;
  private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);

  AlarmArt(Context context, String kind, int tint) {
    super(context);
    this.kind = kind;
    this.tint = tint;
  }

  void tint(int color) {
    tint = color;
    invalidate();
  }

  @Override
  protected void onDraw(Canvas canvas) {
    super.onDraw(canvas);
    int save = canvas.save();
    float width = getWidth() - getPaddingLeft() - getPaddingRight();
    float height = getHeight() - getPaddingTop() - getPaddingBottom();
    float size = Math.min(width, height);
    canvas.translate(getPaddingLeft() + (width - size) / 2, getPaddingTop() + (height - size) / 2);
    canvas.scale(size / 48f, size / 48f);
    paint.setColor(tint);
    paint.setStrokeWidth(3.5f);
    paint.setStrokeCap(Paint.Cap.ROUND);
    paint.setStrokeJoin(Paint.Join.ROUND);
    paint.setStyle(Paint.Style.STROKE);
    if (kind.equals("sort")) {
      canvas.drawLine(7, 12, 40, 12, paint);
      canvas.drawLine(7, 24, 30, 24, paint);
      canvas.drawLine(7, 36, 20, 36, paint);
    } else if (kind.equals("trash")) {
      canvas.drawRoundRect(new RectF(13, 13, 35, 41), 2, 2, paint);
      canvas.drawLine(9, 10, 39, 10, paint);
      canvas.drawLine(19, 6, 29, 6, paint);
      canvas.drawLine(19, 6, 19, 10, paint);
      canvas.drawLine(29, 6, 29, 10, paint);
    } else if (kind.equals("more") || kind.equals("more-horizontal")) {
      paint.setStyle(Paint.Style.FILL);
      for (int n = 0; n < 3; n++)
        canvas.drawCircle(
            kind.equals("more") ? 24 : 13 + n * 11,
            kind.equals("more") ? 13 + n * 11 : 24,
            2.8f,
            paint);
    } else if (kind.equals("chevron")) {
      canvas.drawLine(19, 12, 31, 24, paint);
      canvas.drawLine(31, 24, 19, 36, paint);
    } else if (kind.equals("phone")) {
      canvas.drawRoundRect(new RectF(14, 5, 34, 43), 3, 3, paint);
      canvas.drawLine(21, 37, 27, 37, paint);
    } else if (kind.equals("tag")) {
      Path path = new Path();
      path.moveTo(7, 15);
      path.lineTo(30, 15);
      path.lineTo(40, 24);
      path.lineTo(30, 33);
      path.lineTo(7, 33);
      path.close();
      paint.setStyle(Paint.Style.FILL);
      canvas.drawPath(path, paint);
    } else {
      boolean filled = kind.equals("alarm-filled");
      if (filled) {
        paint.setStyle(Paint.Style.FILL);
        canvas.drawCircle(24, 27, 15, paint);
        paint.setStyle(Paint.Style.STROKE);
      } else canvas.drawCircle(24, 27, 15, paint);
      canvas.drawLine(8, 10, 14, 6, paint);
      canvas.drawLine(34, 6, 40, 10, paint);
      canvas.drawLine(14, 40, 11, 44, paint);
      canvas.drawLine(34, 40, 37, 44, paint);
      if (filled) paint.setColor(Color.BLACK);
      if (kind.equals("clock-plus")) {
        canvas.drawLine(24, 20, 24, 34, paint);
        canvas.drawLine(17, 27, 31, 27, paint);
      } else {
        canvas.drawLine(24, 17, 24, 27, paint);
        canvas.drawLine(24, 27, 31, 31, paint);
      }
    }
    canvas.restoreToCount(save);
  }
}
