package com.vividlands.ragnarok.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.vividlands.ragnarok.classes.Classes;
import com.vividlands.ragnarok.classes.NorseClass;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.fabricmc.fabric.api.networking.v1.PacketByteBufs;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.FriendlyByteBuf;
import org.lwjgl.glfw.GLFW;

/** Ability keys (Z X C V by default) and the class HUD next to the hotbar. */
final class ClassClient {
    private ClassClient() {
    }

    private static final KeyMapping[] KEYS = new KeyMapping[4];
    private static final int[] DEFAULT = {GLFW.GLFW_KEY_Z, GLFW.GLFW_KEY_X, GLFW.GLFW_KEY_C, GLFW.GLFW_KEY_V};

    // last state sent by the server
    static int active = -1, level, xp, xpNeed;
    static final int[] left = new int[4], total = new int[4];

    static void init() {
        for (int i = 0; i < 4; i++) {
            KEYS[i] = KeyBindingHelper.registerKeyBinding(new KeyMapping("key.vividlands_ragnarok.ability" + (i + 1),
                    InputConstants.Type.KEYSYM, DEFAULT[i], "key.categories.vividlands_ragnarok.classes"));
        }
        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            for (int i = 0; i < 4; i++) {
                while (KEYS[i].consumeClick()) {
                    FriendlyByteBuf buf = PacketByteBufs.create();
                    buf.writeVarInt(i);
                    ClientPlayNetworking.send(Classes.CAST, buf);
                }
                if (left[i] > 0) left[i]--;
            }
        });
        ClientPlayNetworking.registerGlobalReceiver(Classes.SYNC, (client, handler, buf, sender) -> {
            int a = buf.readVarInt();
            int lv = 0, x = 0, need = 0;
            int[] l = new int[4], t = new int[4];
            if (a >= 0) {
                lv = buf.readVarInt();
                x = buf.readVarInt();
                need = buf.readVarInt();
                for (int i = 0; i < 4; i++) {
                    l[i] = buf.readVarInt();
                    t[i] = buf.readVarInt();
                }
            }
            int fa = a, flv = lv, fx = x, fn = need;
            client.execute(() -> {
                active = fa;
                level = flv;
                xp = fx;
                xpNeed = fn;
                System.arraycopy(l, 0, left, 0, 4);
                System.arraycopy(t, 0, total, 0, 4);
            });
        });
        HudRenderCallback.EVENT.register(ClassClient::render);
    }

    private static void render(GuiGraphics g, float tickDelta) {
        Minecraft mc = Minecraft.getInstance();
        if (active < 0 || mc.options.hideGui || mc.player == null || mc.player.isSpectator()) return;
        NorseClass c = NorseClass.values()[active];
        Font font = mc.font;
        int w = g.guiWidth(), h = g.guiHeight();
        int x0 = w / 2 + 96, y0 = h - 42;                 // right of the hotbar
        int col = 0xFF000000 | c.color;
        g.drawString(font, c.title + "  Lv " + level, x0, y0, col, true);
        // xp bar
        int bw = 4 * 22 - 2;
        g.fill(x0, y0 + 10, x0 + bw, y0 + 13, 0xAA000000);
        if (xpNeed > 0 && level < NorseClass.MAX_LEVEL) g.fill(x0, y0 + 10, x0 + bw * xp / xpNeed, y0 + 13, col);
        else g.fill(x0, y0 + 10, x0 + bw, y0 + 13, 0xFFE0B65A);
        // ability slots
        for (int i = 0; i < 4; i++) {
            int sx = x0 + i * 22, sy = y0 + 16;
            NorseClass.Ability a = c.abilities.get(i);
            boolean locked = level < a.unlock();
            g.fill(sx, sy, sx + 20, sy + 20, 0xCC10161E);
            g.renderOutline(sx, sy, 20, 20, locked ? 0xFF3A4656 : col);
            if (!locked && left[i] > 0 && total[i] > 0) {
                int hgt = 20 * left[i] / Math.max(1, total[i]);
                g.fill(sx + 1, sy + 20 - hgt, sx + 19, sy + 19, 0x99000000);
                String s = String.valueOf((left[i] + 19) / 20);
                g.drawCenteredString(font, s, sx + 10, sy + 6, 0xFFFFFFFF);
            } else {
                String key = locked ? String.valueOf(a.unlock()) : KEYS[i].getTranslatedKeyMessage().getString();
                if (key.length() > 2) key = key.substring(0, 2);
                g.drawCenteredString(font, key, sx + 10, sy + 6, locked ? 0xFF5A6676 : 0xFFECE3CF);
            }
        }
    }
}
