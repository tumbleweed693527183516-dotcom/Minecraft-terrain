package com.vividlands.ragnarok.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.vividlands.ragnarok.boss.Bosses;
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
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import org.lwjgl.glfw.GLFW;

/** Ability keys, the K class screen, the class panel right of the hotbar, and the Norse pop-ups. */
public final class ClassClient {
    private ClassClient() {
    }

    private static final KeyMapping[] KEYS = new KeyMapping[4];
    private static final int[] DEFAULT = {GLFW.GLFW_KEY_Z, GLFW.GLFW_KEY_X, GLFW.GLFW_KEY_C, GLFW.GLFW_KEY_V};
    private static KeyMapping screenKey;

    // last state sent by the server
    public static int active = -1, level, xp, xpNeed;
    public static final int[] levels = new int[NorseClass.values().length];
    static final int[] left = new int[4], total = new int[4];

    // act banner
    private static Component bannerTitle, bannerSub;
    private static long bannerUntil;

    static String keyName(int i) {
        String k = KEYS[i].getTranslatedKeyMessage().getString();
        return k.length() > 3 ? k.substring(0, 3) : k;
    }

    static void init() {
        for (int i = 0; i < 4; i++) {
            KEYS[i] = KeyBindingHelper.registerKeyBinding(new KeyMapping("key.vividlands_ragnarok.ability" + (i + 1),
                    InputConstants.Type.KEYSYM, DEFAULT[i], "key.categories.vividlands_ragnarok.classes"));
        }
        screenKey = KeyBindingHelper.registerKeyBinding(new KeyMapping("key.vividlands_ragnarok.class_screen",
                InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_K, "key.categories.vividlands_ragnarok.classes"));
        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            for (int i = 0; i < 4; i++) {
                while (KEYS[i].consumeClick()) {
                    FriendlyByteBuf buf = PacketByteBufs.create();
                    buf.writeVarInt(i);
                    ClientPlayNetworking.send(Classes.CAST, buf);
                }
                if (left[i] > 0) left[i]--;
            }
            while (screenKey.consumeClick()) {
                if (mc.screen == null) mc.setScreen(new ClassScreen());
            }
        });
        ClientPlayNetworking.registerGlobalReceiver(Classes.SYNC, (client, handler, buf, sender) -> {
            int[] lv = new int[levels.length];
            for (int i = 0; i < lv.length; i++) lv[i] = buf.readVarInt();
            int a = buf.readVarInt();
            int l = 0, x = 0, need = 0;
            int[] cl = new int[4], ct = new int[4];
            if (a >= 0) {
                l = buf.readVarInt();
                x = buf.readVarInt();
                need = buf.readVarInt();
                for (int i = 0; i < 4; i++) {
                    cl[i] = buf.readVarInt();
                    ct[i] = buf.readVarInt();
                }
            }
            int fa = a, fl = l, fx = x, fn = need;
            client.execute(() -> {
                System.arraycopy(lv, 0, levels, 0, levels.length);
                active = fa;
                level = fl;
                xp = fx;
                xpNeed = fn;
                System.arraycopy(cl, 0, left, 0, 4);
                System.arraycopy(ct, 0, total, 0, 4);
            });
        });
        ClientPlayNetworking.registerGlobalReceiver(Bosses.POPUP, (client, handler, buf, sender) -> {
            int kind = buf.readVarInt();
            if (kind == 0) {
                int act = buf.readVarInt();
                client.execute(() -> actBanner(act));
            } else if (kind == 1) {
                String boss = buf.readUtf();
                int dx = buf.readVarInt(), dz = buf.readVarInt();
                client.execute(() -> client.getToasts().addToast(NorseToast.beast(boss, dx, dz)));
            } else if (kind == 2) {
                int cls = buf.readVarInt(), lv = buf.readVarInt();
                String unlocked = buf.readUtf();
                client.execute(() -> client.getToasts().addToast(NorseToast.levelUp(NorseClass.values()[cls], lv, unlocked)));
            }
        });
        HudRenderCallback.EVENT.register(ClassClient::render);
    }

    static final String[] ACTS = {"", "Act I · Forest and Plain", "Act II · Rivers and Claws", "Act III · The Far Lands",
            "Act IV · The Titans", "Skadi's Hunt is complete"};

    static void actBanner(int act) {
        Minecraft mc = Minecraft.getInstance();
        bannerTitle = Component.literal(ACTS[Math.min(act, ACTS.length - 1)]);
        bannerSub = Component.literal(act <= 4 ? "Five new beasts now roam Midgard" : "Bring the Frozen Heart to Skadi");
        bannerUntil = mc.level == null ? 0 : mc.level.getGameTime() + 120;
    }

    private static void render(GuiGraphics g, float tickDelta) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.options.hideGui || mc.player == null || mc.player.isSpectator()) return;
        Font font = mc.font;
        int w = g.guiWidth(), h = g.guiHeight();
        // act banner
        if (bannerTitle != null && mc.level != null && mc.level.getGameTime() < bannerUntil) {
            long leftT = bannerUntil - mc.level.getGameTime();
            int alpha = (int) Math.min(255, Math.min(leftT, 120 - leftT) * 12 + 10);
            g.pose().pushPose();
            g.pose().translate(w / 2f, 30, 0);
            NorseUI.rule(g, 0, 0, 150);
            g.pose().scale(2, 2, 1);
            g.drawCenteredString(font, bannerTitle, 0, 5, NorseUI.withAlpha(0xE0B65A, alpha));
            g.pose().popPose();
            g.drawCenteredString(font, bannerSub, w / 2, 58, NorseUI.withAlpha(0xC9D4DE, alpha));
        }
        if (active < 0) return;
        NorseClass c = NorseClass.values()[active];
        int col = 0xFF000000 | c.color;
        int x0 = w / 2 + 98, y0 = h - 49;                  // right of the hotbar
        // title: rune, name, level
        g.pose().pushPose();
        g.pose().translate(x0, y0 - 2, 0);
        g.pose().scale(0.5f, 0.5f, 1);
        g.renderItem(new ItemStack(Classes.RUNES.get(c)), 0, 0);
        g.pose().popPose();
        g.drawString(font, c.title, x0 + 11, y0, col, true);
        g.drawString(font, String.valueOf(level), x0 + 13 + font.width(c.title), y0, NorseUI.BONE, true);
        // xp
        float frac = level >= NorseClass.MAX_LEVEL || xpNeed <= 0 ? 1f : xp / (float) xpNeed;
        NorseUI.bar(g, x0, y0 + 10, 4 * 23 - 3, 2, frac, col, 0);
        // ability slots
        for (int i = 0; i < 4; i++) {
            int sx = x0 + i * 23, sy = y0 + 15;
            NorseClass.Ability a = c.abilities.get(i);
            boolean locked = level < a.unlock();
            boolean ready = !locked && left[i] <= 0;
            g.fill(sx, sy, sx + 20, sy + 20, 0xE010161D);
            NorseUI.outline(g, sx, sy, 20, 20, locked ? NorseUI.LOCKED : col);
            if (locked) {
                g.drawCenteredString(font, String.valueOf(a.unlock()), sx + 10, sy + 6, NorseUI.LOCKED_TEXT);
            } else {
                g.drawCenteredString(font, a.glyph(), sx + 10, sy + 6, col);
                if (left[i] > 0 && total[i] > 0) {
                    int hgt = Math.max(1, 18 * left[i] / total[i]);
                    g.fill(sx + 1, sy + 19 - hgt, sx + 19, sy + 19, 0xC0080C10);
                    g.drawCenteredString(font, String.valueOf((left[i] + 19) / 20), sx + 10, sy + 6, NorseUI.BONE);
                }
            }
            g.pose().pushPose();
            g.pose().translate(sx + 10, sy + 22, 0);
            g.pose().scale(0.5f, 0.5f, 1);
            g.drawCenteredString(font, keyName(i), 0, 0, ready ? 0xFFC9D4DE : NorseUI.LOCKED_TEXT);
            g.pose().popPose();
        }
    }
}
