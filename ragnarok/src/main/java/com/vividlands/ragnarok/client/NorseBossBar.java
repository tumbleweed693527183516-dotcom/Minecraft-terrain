package com.vividlands.ragnarok.client;

import com.vividlands.ragnarok.armor.ArmorTraits;
import com.vividlands.ragnarok.boss.Bosses;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.LerpingBossEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** The Norse boss bar: framed health bar with the phase-2 notch, a phase tag, the stagger meter and your ward. */
public final class NorseBossBar {
    private NorseBossBar() {
    }

    record State(String boss, boolean phase2, float poise, boolean stunned, long seen) {
    }

    static final Map<UUID, State> STATES = new HashMap<>();

    static void init() {
        ClientPlayNetworking.registerGlobalReceiver(Bosses.HUD, (client, handler, buf, sender) -> {
            UUID id = buf.readUUID();
            String boss = buf.readUtf();
            boolean p2 = buf.readBoolean();
            float poise = buf.readFloat();
            boolean stunned = buf.readBoolean();
            client.execute(() -> STATES.put(id, new State(boss, p2, poise, stunned, System.currentTimeMillis())));
        });
    }

    public static boolean isOurs(UUID id) {
        State s = STATES.get(id);
        return s != null && System.currentTimeMillis() - s.seen() < 5000;
    }

    /** Draws one of our bars at y; returns the height used. */
    public static int draw(GuiGraphics g, LerpingBossEvent event, int y) {
        Minecraft mc = Minecraft.getInstance();
        Font f = mc.font;
        State s = STATES.get(event.getId());
        int w = g.guiWidth(), bw = 182, x = (w - bw) / 2;
        // name and phase tag
        String name = event.getName().getString();
        int nw = f.width(name);
        int tagW = s.phase2() ? f.width("PHASE II") + 6 : 0;
        int nx = w / 2 - (nw + (tagW > 0 ? tagW + 6 : 0)) / 2;
        g.drawString(f, name, nx, y, NorseUI.BONE, true);
        if (tagW > 0) {
            int tx = nx + nw + 6;
            g.fill(tx, y - 1, tx + tagW, y + 9, NorseUI.BLOOD);
            g.drawString(f, "PHASE II", tx + 3, y, 0xFF10161D, false);
        }
        // health
        int by = y + 12;
        NorseUI.bar(g, x, by, bw, 5, event.getProgress(), NorseUI.BLOOD, NorseUI.BRONZE);
        g.fill(x + bw / 2, by - 3, x + bw / 2 + 1, by + 8, NorseUI.GOLD);     // phase-2 notch
        // stagger and ward
        int ry = by + 10;
        if (s.stunned()) {
            g.drawString(f, "Staggered!", x, ry, NorseUI.GOLD, true);
        } else {
            g.pose().pushPose();
            g.pose().translate(x, ry + 1, 0);
            g.pose().scale(0.5f, 0.5f, 1);
            g.drawString(f, "STAGGER", 0, 0, 0xFFC9D4DE, true);
            g.pose().popPose();
            NorseUI.bar(g, x + 24, ry + 1, 50, 2, s.poise(), NorseUI.GOLD, 0);
        }
        Integer stage = ArmorTraits.BOSS_STAGE.get(s.boss());
        if (stage != null && mc.player != null) {
            int gap = stage - ArmorTraits.ward(mc.player);
            String text = gap <= 0 ? "Ward matched · hits halved" : gap == 1 ? "Ward one stage behind" : "Ward too weak · hits hurt more";
            int color = gap <= 0 ? NorseUI.GREEN : gap == 1 ? NorseUI.GOLD : 0xFFE07A66;
            g.pose().pushPose();
            g.pose().translate(x + bw, ry + 1, 0);
            g.pose().scale(0.5f, 0.5f, 1);
            g.drawString(f, text, -f.width(text), 0, color, true);
            g.pose().popPose();
        }
        return 30;
    }
}
