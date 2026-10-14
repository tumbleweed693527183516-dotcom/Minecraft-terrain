package com.vividlands;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/** Real-world mountain height grids baked into the mod (see tools/stamps/fetch_stamps.py). */
public final class StampLibrary {
    private static final String ROOT = "/vividlands_stamps/";
    private static List<Stamp> stamps = List.of();
    private static double maxHeight = 0;

    private StampLibrary() {
    }

    public record Stamp(String name, int size, double blocksPerPx, double heightUnits, float[] grid) {
        /** Bilinear sample in grid pixels; 0 outside the grid. */
        public double sample(double px, double pz) {
            if (px < 0 || pz < 0 || px >= size - 1 || pz >= size - 1) {
                return 0;
            }
            int ix = (int) px, iz = (int) pz;
            double fx = px - ix, fz = pz - iz;
            int i = iz * size + ix;
            double a = grid[i] + (grid[i + 1] - grid[i]) * fx;
            double b = grid[i + size] + (grid[i + size + 1] - grid[i + size]) * fx;
            return a + (b - a) * fz;
        }
    }

    public static List<Stamp> all() {
        return stamps;
    }

    public static double maxHeight() {
        return maxHeight;
    }

    static void load() {
        List<Stamp> loaded = new ArrayList<>();
        try (InputStream in = open("stamps.json")) {
            JsonArray list = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray();
            for (JsonElement e : list) {
                JsonObject o = e.getAsJsonObject();
                int size = o.get("size").getAsInt();
                float[] grid = new float[size * size];
                try (DataInputStream data = new DataInputStream(open(o.get("file").getAsString()))) {
                    for (int i = 0; i < grid.length; i++) {
                        grid[i] = data.readUnsignedShort() / 65535f;
                    }
                }
                Stamp s = new Stamp(o.get("name").getAsString(), size, o.get("blocks_per_px").getAsDouble(),
                        o.get("height_units").getAsDouble(), grid);
                loaded.add(s);
                maxHeight = Math.max(maxHeight, s.heightUnits());
            }
        } catch (IOException | RuntimeException ex) {
            VividLands.LOG.error("Could not load mountain stamps; real-world mountains will be missing", ex);
        }
        stamps = List.copyOf(loaded);
        VividLands.LOG.info("Loaded {} real-world mountain stamps", stamps.size());
    }

    private static InputStream open(String file) throws IOException {
        InputStream in = StampLibrary.class.getResourceAsStream(ROOT + file);
        if (in == null) {
            throw new IOException("missing resource " + ROOT + file);
        }
        return in;
    }
}
