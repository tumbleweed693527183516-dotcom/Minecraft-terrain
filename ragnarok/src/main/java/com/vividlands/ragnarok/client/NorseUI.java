package com.vividlands.ragnarok.client;

import net.minecraft.client.gui.GuiGraphics;

/** The approved Norse look, drawn with plain fills: slate panels, bronze border with a dark rim, gold corner diamonds. */
public final class NorseUI {
    private NorseUI() {
    }

    public static final int SLATE = 0xF018202A, SLATE_DARK = 0xF0141A21, RIM = 0xFF0C1116, BRONZE = 0xFFA8793A,
            GOLD = 0xFFE0B65A, BONE = 0xFFECE3CF, MIST = 0xFF94A6B8, BLOOD = 0xFFC8553D, FROST = 0xFF7FC8D6,
            GREEN = 0xFF7CC28C, LOCKED = 0xFF2C3A4A, LOCKED_TEXT = 0xFF6B7A8A;

    /** A framed panel; {@code border} is usually BRONZE (BLOOD for boss things). */
    public static void panel(GuiGraphics g, int x, int y, int w, int h, int border, int fill) {
        panel(g, x, y, w, h, border, fill, 0);
    }

    public static void panel(GuiGraphics g, int x, int y, int w, int h, int border, int fill, int z) {
        g.fill(x - 2, y - 2, x + w + 2, y + h + 2, z, RIM);          // outer rim
        g.fill(x - 1, y - 1, x + w + 1, y + h + 1, z, border);       // bronze line
        g.fill(x, y, x + w, y + h, z, RIM);                          // inner rim
        g.fill(x + 1, y + 1, x + w - 1, y + h - 1, z, fill);
        diamond(g, x - 1, y - 1, z);
        diamond(g, x + w, y - 1, z);
        diamond(g, x - 1, y + h, z);
        diamond(g, x + w, y + h, z);
    }

    /** A small gold diamond centred on (cx, cy). */
    public static void diamond(GuiGraphics g, int cx, int cy, int z) {
        g.fill(cx, cy - 2, cx + 1, cy + 3, z, GOLD);
        g.fill(cx - 1, cy - 1, cx + 2, cy + 2, z, GOLD);
        g.fill(cx - 2, cy, cx + 3, cy + 1, z, GOLD);
    }

    /** A bar with a dark trough; {@code frame} 0 for none. */
    public static void bar(GuiGraphics g, int x, int y, int w, int h, float fill, int color, int frame) {
        if (frame != 0) {
            g.fill(x - 2, y - 2, x + w + 2, y + h + 2, RIM);
            g.fill(x - 1, y - 1, x + w + 1, y + h + 1, frame);
        }
        g.fill(x, y, x + w, y + h, 0xD80C1116);
        int f = Math.round(w * Math.max(0, Math.min(1, fill)));
        if (f > 0) g.fill(x, y, x + f, y + h, color);
    }

    public static void outline(GuiGraphics g, int x, int y, int w, int h, int color) {
        g.fill(x, y, x + w, y + 1, color);
        g.fill(x, y + h - 1, x + w, y + h, color);
        g.fill(x, y, x + 1, y + h, color);
        g.fill(x + w - 1, y, x + w, y + h, color);
    }

    /** Thin rule with a gold diamond in the middle (banners). */
    public static void rule(GuiGraphics g, int cx, int y, int half) {
        g.fill(cx - half, y, cx - 6, y + 1, BRONZE);
        g.fill(cx + 6, y, cx + half, y + 1, BRONZE);
        diamond(g, cx, y, 0);
    }

    public static int withAlpha(int rgb, int alpha) {
        return (alpha << 24) | (rgb & 0xFFFFFF);
    }
}
