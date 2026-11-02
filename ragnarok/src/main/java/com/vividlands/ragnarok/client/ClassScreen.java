package com.vividlands.ragnarok.client;

import com.vividlands.ragnarok.classes.Classes;
import com.vividlands.ragnarok.classes.NorseClass;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** The class screen (K): the five paths with your level in each, and the chosen path's passive and abilities. */
public class ClassScreen extends Screen {
    private int shown;

    public ClassScreen() {
        super(Component.literal("Paths of the Einherjar"));
        shown = Math.max(0, ClassClient.active);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    private static final int W = 440, H = 236;

    /** Shrinks the whole panel on small screens instead of letting it spill over. */
    private float scale() { return Math.min(1f, Math.min((width - 16) / (float) W, (height - 24) / (float) H)); }
    private int pw() { return W; }
    private int ph() { return H; }
    private int px() { return Math.round((width / scale() - W) / 2); }
    private int py() { return Math.round((height / scale() - H) / 2); }

    @Override
    public boolean mouseClicked(double rawX, double rawY, int button) {
        double mx = rawX / scale(), my = rawY / scale();
        int x = px() + 8, y = py() + 20;
        for (int i = 0; i < NorseClass.values().length; i++) {
            if (mx >= x && mx < x + 92 && my >= y + i * 22 && my < y + i * 22 + 20) {
                shown = i;
                return true;
            }
        }
        return super.mouseClicked(rawX, rawY, button);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
        renderBackground(g);
        float sc = scale();
        g.pose().pushPose();
        g.pose().scale(sc, sc, 1);
        mouseX = Math.round(mouseX / sc);
        mouseY = Math.round(mouseY / sc);
        Font f = font;
        int x = px(), y = py(), w = pw(), h = ph();
        NorseUI.panel(g, x, y, w, h, NorseUI.BRONZE, NorseUI.SLATE);
        // left: the paths
        g.drawString(f, "PATHS", x + 12, y + 8, NorseUI.MIST, false);
        g.fill(x + 104, y + 6, x + 105, y + h - 6, NorseUI.LOCKED);
        NorseClass[] all = NorseClass.values();
        for (int i = 0; i < all.length; i++) {
            NorseClass c = all[i];
            int ry = y + 20 + i * 22;
            boolean sel = i == shown;
            if (sel) {
                g.fill(x + 8, ry, x + 100, ry + 20, 0xFF222C38);
                NorseUI.outline(g, x + 8, ry, 92, 20, 0xFF000000 | c.color);
            } else if (mouseX >= x + 8 && mouseX < x + 100 && mouseY >= ry && mouseY < ry + 20) {
                g.fill(x + 8, ry, x + 100, ry + 20, 0x60222C38);
            }
            g.renderItem(new ItemStack(Classes.RUNES.get(c)), x + 10, ry + 2);
            g.drawString(f, c.title, x + 30, ry + 6, i == ClassClient.active ? (0xFF000000 | c.color) : NorseUI.BONE, false);
            String lv = String.valueOf(Math.max(1, ClassClient.levels[i]));
            g.drawString(f, lv, x + 96 - f.width(lv), ry + 6, NorseUI.MIST, false);
        }
        g.drawWordWrap(f, Component.literal("Switch with a rune stone. Every path keeps its own level."), x + 12, y + 136, 86, NorseUI.MIST);

        // right: the chosen path
        NorseClass c = all[shown];
        int col = 0xFF000000 | c.color;
        int cx = x + 114, cw = w - 124;
        int lvl = Math.max(1, ClassClient.levels[shown]);
        g.pose().pushPose();
        g.pose().translate(cx, y + 8, 0);
        g.pose().scale(1.5f, 1.5f, 1);
        g.renderItem(new ItemStack(Classes.RUNES.get(c)), 0, 0);
        g.drawString(f, c.title, 20, 1, col, false);
        g.pose().popPose();
        g.drawString(f, "Level " + lvl + " of " + NorseClass.MAX_LEVEL, cx + 30, y + 24, NorseUI.BONE, false);
        if (shown == ClassClient.active) {
            float frac = lvl >= NorseClass.MAX_LEVEL || ClassClient.xpNeed <= 0 ? 1f : ClassClient.xp / (float) ClassClient.xpNeed;
            NorseUI.bar(g, cx + 140, y + 26, cw - 140, 4, frac, col, 0);
        } else {
            g.drawString(f, "not active", cx + cw - f.width("not active"), y + 24, NorseUI.MIST, false);
        }
        // passive
        int py = y + 40;
        g.fill(cx, py, cx + cw, py + 16, NorseUI.SLATE_DARK);
        g.drawString(f, c.passive + ":", cx + 5, py + 4, NorseUI.BONE, false);
        g.drawString(f, f.plainSubstrByWidth(c.passiveText, cw - 12 - f.width(c.passive + ": ")), cx + 8 + f.width(c.passive + ":"), py + 4, NorseUI.MIST, false);
        // abilities
        for (int i = 0; i < 4; i++) {
            NorseClass.Ability a = c.abilities.get(i);
            int ry = py + 22 + i * 42;
            boolean locked = lvl < a.unlock();
            g.fill(cx, ry, cx + cw, ry + 40, locked ? 0xC0141A21 : 0xE01D2632);
            NorseUI.outline(g, cx, ry, cw, 40, NorseUI.LOCKED);
            g.fill(cx + 4, ry + 8, cx + 28, ry + 32, 0xFF10161D);
            NorseUI.outline(g, cx + 4, ry + 8, 24, 24, locked ? NorseUI.LOCKED : col);
            if (locked) g.drawCenteredString(f, String.valueOf(a.unlock()), cx + 16, ry + 16, NorseUI.LOCKED_TEXT);
            else g.drawCenteredString(f, a.glyph(), cx + 16, ry + 16, col);
            String key = i < 4 ? ClassClient.keyName(i) : "";
            g.drawString(f, a.name(), cx + 34, ry + 5, locked ? NorseUI.MIST : NorseUI.BONE, false);
            String sub = locked ? "unlocks at level " + a.unlock() : key + " · level " + a.unlock();
            g.drawString(f, sub, cx + 38 + f.width(a.name()), ry + 5, NorseUI.LOCKED_TEXT, false);
            String cd = Math.round(a.cooldownSeconds() * NorseClass.lerp(lvl, 1.0, 0.6)) + " s";
            g.drawString(f, cd, cx + cw - 6 - f.width(cd), ry + 5, locked ? NorseUI.LOCKED_TEXT : NorseUI.MIST, false);
            String now = a.nowAt(lvl);
            String line = a.text();
            g.drawString(f, f.plainSubstrByWidth(line, cw - 40), cx + 34, ry + 17, locked ? NorseUI.LOCKED_TEXT : 0xFFC9D4DE, false);
            if (now != null) {
                g.drawString(f, (locked ? "At level " + a.unlock() + ": " : "Now: ") + a.nowAt(Math.max(lvl, a.unlock())),
                        cx + 34, ry + 28, locked ? NorseUI.LOCKED_TEXT : NorseUI.GOLD, false);
            }
        }
        g.drawCenteredString(f, "K or Esc to close", x + w / 2, y + h + 6, NorseUI.MIST);
        g.pose().popPose();
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (minecraft != null && minecraft.options != null && key == org.lwjgl.glfw.GLFW.GLFW_KEY_K) {
            onClose();
            return true;
        }
        return super.keyPressed(key, scan, mods);
    }
}
