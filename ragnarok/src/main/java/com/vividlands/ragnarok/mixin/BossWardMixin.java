package com.vividlands.ragnarok.mixin;

import com.vividlands.ragnarok.armor.ArmorTraits;
import com.vividlands.ragnarok.boss.Bosses;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Boss Ward: a boss's hits on a player are scaled by how well the player's armor matches the boss (ArmorTraits). */
@Mixin(LivingEntity.class)
public abstract class BossWardMixin {
    @ModifyVariable(method = "hurt", at = @At("HEAD"), argsOnly = true)
    private float vlr$bossWard(float amount, DamageSource source, float original) {
        if (!((Object) this instanceof Player player) || amount <= 0) return amount;
        String boss = Bosses.bossId(source.getEntity());
        if (boss == null) return amount;
        return amount * ArmorTraits.wardMultiplier(player, boss);
    }
}
