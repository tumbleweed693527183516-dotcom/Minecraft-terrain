package com.vividlands.ragnarok.client.mixin;

import com.vividlands.ragnarok.client.NorseBossBar;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.BossHealthOverlay;
import net.minecraft.client.gui.components.LerpingBossEvent;
import net.minecraft.world.BossEvent;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.Map;
import java.util.UUID;

/** Our bosses get the Norse bar; every other boss bar is drawn as vanilla does. */
@Mixin(BossHealthOverlay.class)
public abstract class BossHealthOverlayMixin {
    @Shadow @Final Map<UUID, LerpingBossEvent> events;
    @Shadow @Final private Minecraft minecraft;

    @Shadow
    protected abstract void drawBar(GuiGraphics g, int x, int y, BossEvent event);

    @Inject(method = "render", at = @At("HEAD"), cancellable = true)
    private void vlr$norseBars(GuiGraphics g, CallbackInfo ci) {
        if (events.isEmpty() || events.keySet().stream().noneMatch(NorseBossBar::isOurs)) return;
        ci.cancel();
        int w = g.guiWidth(), y = 12;
        for (LerpingBossEvent e : events.values()) {
            if (NorseBossBar.isOurs(e.getId())) {
                y += NorseBossBar.draw(g, e, y - 9) + 4;
            } else {
                int x = w / 2 - 91;
                drawBar(g, x, y, e);
                g.drawString(minecraft.font, e.getName(), w / 2 - minecraft.font.width(e.getName()) / 2, y - 9, 0xFFFFFF);
                y += 10 + minecraft.font.lineHeight;
            }
            if (y >= g.guiHeight() / 3) break;
        }
    }
}
