package com.vividlands.ragnarok.mixin;

import com.vividlands.ragnarok.Ragnarok;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Nothing travels to the Nether or the End (covers portals left by structures or other mods). */
@Mixin(Entity.class)
public abstract class EntityDimensionMixin {
    @Inject(method = "changeDimension", at = @At("HEAD"), cancellable = true)
    private void ragnarok$closed(ServerLevel destination, CallbackInfoReturnable<Entity> cir) {
        if (Ragnarok.closed(destination.dimension())) {
            cir.setReturnValue(null);
        }
    }
}
