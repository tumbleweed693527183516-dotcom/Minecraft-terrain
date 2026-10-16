package com.vividlands.ragnarok.mixin;

import com.vividlands.ragnarok.Ragnarok;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Players can't travel to the Nether or the End either (ServerPlayer overrides changeDimension). */
@Mixin(ServerPlayer.class)
public abstract class ServerPlayerDimensionMixin {
    @Inject(method = "changeDimension", at = @At("HEAD"), cancellable = true)
    private void ragnarok$closed(ServerLevel destination, CallbackInfoReturnable<Entity> cir) {
        if (Ragnarok.closed(destination.dimension())) {
            ((ServerPlayer) (Object) this).displayClientMessage(
                    Component.literal("That realm is sealed until Ragnarok."), true);
            cir.setReturnValue(null);
        }
    }
}
