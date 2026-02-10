
import org.schabi.newpipe.extractor.NewPipe;
import org.schabi.newpipe.extractor.ServiceList;
import org.schabi.newpipe.extractor.downloader.Downloader;
import org.schabi.newpipe.extractor.downloader.Request;
import org.schabi.newpipe.extractor.downloader.Response;
import org.schabi.newpipe.extractor.stream.StreamInfo;
import org.schabi.newpipe.extractor.stream.VideoStream;
import org.schabi.newpipe.extractor.stream.AudioStream;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

public class Main {

    /**
     * Correct Downloader for NewPipeExtractor (Java-only, YouTube-safe)
     */
    static class SimpleDownloader extends Downloader {

        @Override
        public Response execute(Request request) {
            try {
                URL url = new URL(request.url());
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();

                conn.setRequestMethod(request.httpMethod());
                conn.setInstanceFollowRedirects(true);
                conn.setConnectTimeout(15_000);
                conn.setReadTimeout(15_000);

                // headers
                for (Map.Entry<String, List<String>> h : request.headers().entrySet()) {
                    for (String v : h.getValue()) {
                        conn.addRequestProperty(h.getKey(), v);
                    }
                }

                // POST body (THIS FIXES HTTP 411)
                if ("POST".equalsIgnoreCase(request.httpMethod())) {
                    byte[] bodyBytes
                            = request.dataToSend() == null
                            ? new byte[0]
                            : request.dataToSend().getBytes(StandardCharsets.UTF_8);

                    conn.setDoOutput(true);
                    conn.setFixedLengthStreamingMode(bodyBytes.length);
                    conn.setRequestProperty("Content-Length", String.valueOf(bodyBytes.length));

                    try (OutputStream os = conn.getOutputStream()) {
                        os.write(bodyBytes);
                    }
                }

                int code = conn.getResponseCode();
                InputStream is = (code >= 400) ? conn.getErrorStream() : conn.getInputStream();

                BufferedReader reader
                        = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8));

                StringBuilder body = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    body.append(line).append('\n');
                }

                return new Response(
                        code,
                        conn.getResponseMessage(),
                        conn.getHeaderFields(),
                        body.toString(),
                        conn.getContentType()
                );

            } catch (Exception e) {
                throw new RuntimeException("Downloader error", e);
            }
        }
    }

    public static void main(String[] args) throws Exception {

        if (args.length == 0) {
            System.out.println("Usage:");
            System.out.println("  java -jar newpipe-cli.jar <youtube-url>");
            return;
        }

        // REQUIRED init
        NewPipe.init(new SimpleDownloader());

        StreamInfo info = StreamInfo.getInfo(ServiceList.YouTube, args[0]);

        System.out.println("TITLE: " + info.getName());

        System.out.println("\nVIDEO STREAMS:");
        for (VideoStream v : info.getVideoStreams()) {
            System.out.println(
                    v.getResolution() + " | "
                    + v.getCodec() + " | "
                    + v.getUrl()
            );
        }

        System.out.println("\nAUDIO STREAMS:");
        for (AudioStream a : info.getAudioStreams()) {
            System.out.println(
                    a.getAverageBitrate() + " | "
                    + a.getCodec() + " | "
                    + a.getUrl()
            );
        }
    }
}
