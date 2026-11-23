// Upstream source: https://github.com/Vanilagy/mediabunny/tree/v1.66.2
import {
  BlobSource, BufferTarget, EncodedPacketSink, EncodedVideoPacketSource,
  Input, MP4, Mp4OutputFormat, Output
} from "./vendor/mediabunny-1.66.2/mediabunny.min.mjs";

// The recorder captures a single silent canvas track. Write one sample table
// covering all MediaRecorder fragments so chat apps can seek to the last stop.
export async function finalizeRouteMp4(recording) {
  const input = new Input({formats: [MP4], source: new BlobSource(recording)});
  try {
    const track = await input.getPrimaryVideoTrack();
    if (!track) throw new Error("Missing canvas track");
    const codec = await track.getCodec();
    const decoderConfig = await track.getDecoderConfig();
    if (!codec || !decoderConfig) throw new Error("Missing video configuration");
    const source = new EncodedVideoPacketSource(codec);
    const target = new BufferTarget();
    const output = new Output({format: new Mp4OutputFormat({fastStart: "in-memory"}), target});
    output.addVideoTrack(source, {decoderConfig});
    await output.start();
    let end = 0;
    for await (const packet of new EncodedPacketSink(track).packets()) {
      await source.add(packet);
      end = Math.max(end, packet.timestamp + packet.duration);
    }
    if (!(end > 0)) throw new Error("Empty recording");
    await output.finalize();
    return {blob: new Blob([target.buffer], {type: "video/mp4"}), duration: end};
  } finally {
    input.dispose();
  }
}
