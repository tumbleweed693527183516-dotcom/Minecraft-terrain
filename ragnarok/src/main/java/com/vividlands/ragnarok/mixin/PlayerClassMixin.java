package com.vividlands.ragnarok.mixin;

import com.vividlands.ragnarok.classes.ClassData;
import com.vividlands.ragnarok.classes.ClassHolder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Gives every player a class record, saved with the player. */
@Mixin(Player.class)
public abstract class PlayerClassMixin implements ClassHolder {
    @Unique
    private final ClassData vlr$classData = new ClassData();

    @Override
    public ClassData vlr$classes() {
        return vlr$classData;
    }

    @Inject(method = "addAdditionalSaveData", at = @At("TAIL"))
    private void vlr$saveClasses(CompoundTag tag, CallbackInfo ci) {
        tag.put("VividClasses", vlr$classData.save());
    }

    @Inject(method = "readAdditionalSaveData", at = @At("TAIL"))
    private void vlr$loadClasses(CompoundTag tag, CallbackInfo ci) {
        if (tag.contains("VividClasses")) vlr$classData.load(tag.getCompound("VividClasses"));
    }
}
