package com.vividlands.ragnarok.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.vividlands.ragnarok.boss.BossHolder;
import com.vividlands.ragnarok.boss.Bosses;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;

/** Every entity can be a boss: remembers which one, and bosses get a bigger hitbox. */
@Mixin(Entity.class)
public abstract class EntityBossMixin implements BossHolder {
    @Unique
    private String vlr$bossId;

    @Override
    public String vlr$boss() {
        return vlr$bossId;
    }

    @Override
    public void vlr$setBoss(String id) {
        vlr$bossId = id;
    }

    @ModifyExpressionValue(method = "refreshDimensions", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/entity/Entity;getDimensions(Lnet/minecraft/world/entity/Pose;)Lnet/minecraft/world/entity/EntityDimensions;"))
    private EntityDimensions vlr$bossSize(EntityDimensions original) {
        if (vlr$bossId == null) return original;
        float s = Bosses.scaleOf((Entity) (Object) this);
        return s == 1f ? original : original.scale(s);
    }
}
