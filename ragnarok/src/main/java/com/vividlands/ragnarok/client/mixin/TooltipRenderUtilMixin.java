package com.vividlands.ragnarok.client.mixin;

import com.vividlands.ragnarok.client.NorseTooltip;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.tooltip.TooltipRenderUtil;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** The pack's own items get the slate-and-bronze tooltip frame. */
@Mixin(TooltipRenderUtil.class)
public abstract class TooltipRenderUtilMixin {
    @Inject(method = "renderTooltipBackground", at = @At("HEAD"), cancellable = true)
    private static void vlr$norseFrame(GuiGraphics g, int x, int y, int w, int h, int z, CallbackInfo ci) {
        if (NorseTooltip.draw(g, x, y, w, h, z)) ci.cancel();
    }
}
