import {readFileSync} from "node:fs";
const root = process.argv[2] || "_site";
const expectedRevision = process.argv[3] || "141";
const html = readFileSync(root + "/index.html", "utf8");
function between(start, end) {
  const a = html.indexOf(start), b = html.indexOf(end, a + start.length);
  if (a < 0 || b < 0) throw new Error("Missing source section: " + start);
  return html.slice(a, b);
}
const helper = between('<script id="rev141-korea-date">', "</script>").replace('<script id="rev141-korea-date">', "");
const calendar = between("let calView=", "function selectedText(");
const data = between("const SUMMER_DATA=", "const ORDER=");
const today = between("const todayKey=", "let state=");
const clock = between("function tick(){", "tick();setInterval(tick");
const midnight = between("/* Rev90: keep", "</script>");
const season = between("/* Rev91: preserve", "</script>");
let instant = "2026-08-31T14:59:59Z";
const NativeDate = Date;
class TestDate extends NativeDate {
  constructor(...args) { if(args.length) super(...args); else super(instant); }
  static now() { return new NativeDate(instant).getTime(); }
}
const elements = new Map();
const listeners = {};
const document = {
  hidden: false, title: "",
  getElementById(id) { if(!elements.has(id)) elements.set(id, {textContent:""}); return elements.get(id); },
  querySelectorAll() { return []; },
  addEventListener(name, cb) { (listeners[name] ||= []).push(cb); }
};
const window = {addEventListener(name, cb) { (listeners[name] ||= []).push(cb); }};
const checks = `
function expect(actual, wanted) {
  if(actual !== wanted) throw new Error(JSON.stringify({actual,wanted}));
}
expect(rev91Season, "summer");
function check(iso, stamp, weekday, schedule, buses) {
  setInstant(iso);
  rev90SelectToday(false);
  rev91SyncSeason(false);
  tick();
  expect(rev90DateStamp(), stamp);
  expect(state.day, schedule);
  expect(DATA[state.day].count, buses);
  expect(document.getElementById("hdr-date").textContent, stamp.replaceAll("-", ".") + " · " + weekday + "요일");
  const n = new TimetableDate();
  expect(n.getTime(), Date.now());
}
check("2026-08-31T15:00:00Z","2026-09-01","화","weekday",13);
expect(rev91Season, "autumn");
check("2026-09-23T15:00:00Z","2026-09-24","목","sunday",8);
check("2026-09-24T15:00:00Z","2026-09-25","금","sunday",8);
check("2026-09-25T15:00:00Z","2026-09-26","토","sunday",8);
check("2026-09-26T15:00:00Z","2026-09-27","일","sunday",8);
check("2026-09-27T15:00:00Z","2026-09-28","월","weekday",13);
check("2026-10-02T15:00:00Z","2026-10-03","토","sunday",8);
check("2026-10-04T15:00:00Z","2026-10-05","월","sunday",8);
check("2026-10-05T15:00:00Z","2026-10-06","화","weekday",13);
check("2026-10-09T15:00:00Z","2026-10-10","토","saturday",9);
expect(lunarInfo(new TimetableDate(2026,8,25)).label, "8.15");
const departure = new TimetableDate("2026-10-04T00:00:00Z");
departure.setHours(10,30,0,0);
expect(departure.getTime(), new Date("2026-10-04T01:30:00Z").getTime());
const rollover = new TimetableDate(2026,11,31);
rollover.setDate(rollover.getDate()+1);
expect(dateKey(rollover), "2027-01-01");
setInstant("2026-10-05T15:00:00Z");
for (const cb of listeners.pageshow || []) cb();
expect(state.day, "weekday");
setInstant("2026-10-08T15:00:00Z");
for (const cb of listeners.visibilitychange || []) cb();
expect(state.day, "sunday");
expect(DATA[state.day].count, 8);
`;
new Function("Date","document","window","location","setInterval","setTimeout","setInstant","listeners",
  helper + calendar + data + today +
  "let state={day:todayKey()};function render(){}\n" +
  clock + midnight + season + checks
)(TestDate, document, window, {search:""}, ()=>{}, ()=>{}, value=>{instant=value;}, listeners);
for (const script of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)) {
  if (/type=["']application\/(?:ld\+)?json["']/i.test(script[1])) JSON.parse(script[2]);
  else new Function(script[2]);
}

if (!html.includes("Rev."+expectedRevision) || !readFileSync(root+"/sw.js","utf8").includes('REVISION="'+expectedRevision+'"')) throw new Error("Revision mismatch");
if (html.includes("rev124TodayIsFiveBus")) throw new Error("Obsolete temporary timetable");
if (Number(expectedRevision) >= 203) {
  const heading = between('<div class="calendar-week"', '</div>');
  const days = Array.from(heading.matchAll(/<span[^>]*>(.)<\/span>/g), match => match[1]).join('');
  if (days !== '월화수목금토일') throw new Error('Work calendar weekdays are out of order');
  const calendarDraw = between('function drawCalendar(){', 'function openCalendar()');
  const draws = [];
  const grid = {appendChild(button) { draws.push(button.label); }};
  const mockDocument = {createElement: () => ({
    classList:{add() {}}, setAttribute(name, value) { this.label = value; }, addEventListener() {}
  })};
  const CalendarDate = new Function(helper + '\nreturn TimetableDate;')();
  const calendarText = day => new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Seoul', year:'numeric', month:'2-digit', day:'2-digit'}).format(day);
  new Function('calView', 'calMonth', 'calendarGrid', 'lunarInfo', 'calendarInfo', 'document', 'sameDate', 'calPicked', 'dateLabel',
    helper + '\n' + calendarDraw + '\ndrawCalendar();')(
    new CalendarDate(2026, 10, 1), {}, grid, () => ({label:''}), () => ({holidays:[], events:[]}), mockDocument, () => false, null, calendarText
  );
  if (!draws[0].startsWith('2026-10-26') || !draws[6].startsWith('2026-11-01') || draws.length !== 42) {
    throw new Error('November 2026 must start in the Sunday column of a Monday-first week');
  }
}
for (const revision of [94,95,96]) {
  const page = readFileSync(root+"/1560_timetable_Rev"+revision+"_KCC_CCTV.html","utf8");
  const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
  let redirected = "";
  new Function("location",script)({
    href:"https://gusibzo.github.io/1560-timetable/1560_timetable_Rev"+revision+"_KCC_CCTV.html?v=96&swfix=96&season=autumn#rows",
    search:"?v=96&swfix=96&season=autumn", hash:"#rows",
    replace(value){redirected=value;}
  });
  if (redirected!=="https://gusibzo.github.io/1560-timetable/?season=autumn#rows") throw new Error("Legacy redirect mismatch");
}
console.log("Rev"+expectedRevision+" Korean date and legacy path checks passed ("+(process.env.TZ||"default")+")");
