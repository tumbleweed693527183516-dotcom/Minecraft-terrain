package com.vividlands.ragnarok.mixin;

import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.EnderEyeItem;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.Blocks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** The End is closed: eyes of ender can't be placed in portal frames (they still fly to strongholds). */
@Mixin(EnderEyeItem.class)
public abstract class EnderEyeItemMixin {
    @Inject(method = "useOn", at = @At("HEAD"), cancellable = true)
    private void ragnarok$noEndPortal(UseOnContext context, CallbackInfoReturnable<InteractionResult> cir) {
        if (context.getLevel().getBlockState(context.getClickedPos()).is(Blocks.END_PORTAL_FRAME)) {
            cir.setReturnValue(InteractionResult.PASS);
        }
    }
}
