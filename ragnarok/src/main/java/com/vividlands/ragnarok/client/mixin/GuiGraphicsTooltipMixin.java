package com.vividlands.ragnarok.client.mixin;

import com.vividlands.ragnarok.client.NorseTooltip;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Remembers which item's tooltip is being drawn, so the frame can be Norse for the pack's own items. */
@Mixin(GuiGraphics.class)
public abstract class GuiGraphicsTooltipMixin {
    @Inject(method = "renderTooltip(Lnet/minecraft/client/gui/Font;Lnet/minecraft/world/item/ItemStack;II)V", at = @At("HEAD"))
    private void vlr$tooltipStart(Font font, ItemStack stack, int x, int y, CallbackInfo ci) {
        NorseTooltip.current = stack;
    }

    @Inject(method = "renderTooltip(Lnet/minecraft/client/gui/Font;Lnet/minecraft/world/item/ItemStack;II)V", at = @At("RETURN"))
    private void vlr$tooltipEnd(Font font, ItemStack stack, int x, int y, CallbackInfo ci) {
        NorseTooltip.current = ItemStack.EMPTY;
    }
}
