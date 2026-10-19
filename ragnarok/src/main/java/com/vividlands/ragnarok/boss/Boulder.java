package com.vividlands.ragnarok.boss;

import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;

/** A boulder thrown by a boss (the Silverback). Drawn as a big cobblestone item; shatters where it lands. */
public class Boulder extends ThrowableItemProjectile {
    private float damage = 8;

    public Boulder(EntityType<? extends Boulder> type, Level level) {
        super(type, level);
    }

    public Boulder(Level level, LivingEntity thrower, float damage) {
        super(Bosses.BOULDER, thrower, level);
        this.damage = damage;
    }

    @Override
    protected Item getDefaultItem() {
        return Items.COBBLESTONE;
    }

    @Override
    protected float getGravity() {
        return 0.045f;
    }

    @Override
    protected void onHitEntity(EntityHitResult hit) {
        super.onHitEntity(hit);
        if (hit.getEntity() instanceof LivingEntity l && !Bosses.isBoss(l) && !Bosses.isMinion(l)) {
            l.hurt(damageSources().thrown(this, getOwner()), damage);
            l.setDeltaMovement(l.getDeltaMovement().add(getDeltaMovement().normalize().scale(0.7)).add(0, 0.3, 0));
            l.hurtMarked = true;
        }
    }

    @Override
    protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel sl) {
            sl.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, Blocks.COBBLESTONE.defaultBlockState()),
                    getX(), getY(), getZ(), 40, 0.4, 0.4, 0.4, 0.2);
            sl.playSound(null, getX(), getY(), getZ(), SoundEvents.STONE_BREAK, SoundSource.HOSTILE, 1.5f, 0.6f);
            discard();
        }
    }
}
