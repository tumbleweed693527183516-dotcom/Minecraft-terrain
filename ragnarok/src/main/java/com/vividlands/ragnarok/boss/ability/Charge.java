package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.HashSet;
import java.util.Set;

/**
 * Lowers its head, then charges in a straight line. Anything it runs into is hurt and thrown. A boss that can't
 * break blocks is stunned when it slams into a wall (dodge the charge next to one!); one that can (the rhino)
 * smashes through soft blocks (dirt, sand, snow, leaves, plants, glass) and is stunned only by hard ones.
 */
public class Charge extends Ability {
    private final int windup, maxTicks, stunTicks;
    private final double speed, damageMul, throwStrength;
    private final boolean breaksBlocks;
    private Vec3 dir = Vec3.ZERO;
    private final Set<LivingEntity> hit = new HashSet<>();

    public Charge(int cooldown, int windup, int maxTicks, double speed, double damageMul, double throwStrength,
                  boolean breaksBlocks, int stunTicks) {
        super(cooldown);
        this.windup = windup;
        this.maxTicks = maxTicks;
        this.speed = speed;
        this.damageMul = damageMul;
        this.throwStrength = throwStrength;
        this.breaksBlocks = breaksBlocks;
        this.stunTicks = stunTicks;
        range(5, 28);
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return super.canStart(f, target) && f.mob().onGround() && f.mob().hasLineOfSight(target);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        hit.clear();
        f.sound(SoundEvents.RAVAGER_ROAR, 1.5f, 1.2f);
        return windup + maxTicks;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Mob m = f.mob();
        if (t < windup) {
            f.freeze();
            f.face(target);
            if (t % 3 == 0) f.particles(ParticleTypes.CAMPFIRE_COSY_SMOKE, m.getX(), m.getY() + 0.2, m.getZ(), 2, 0.5, 0.1, 0.5, 0.01);
            if (t == windup - 1) {
                dir = new Vec3(target.getX() - m.getX(), 0, target.getZ() - m.getZ()).normalize();
            }
            return;
        }
        m.getNavigation().stop();
        double s = speed * (f.enraged() ? 1.2 : 1);
        m.setDeltaMovement(dir.x * s, m.getDeltaMovement().y, dir.z * s);
        float yaw = (float) (Math.atan2(dir.z, dir.x) * 180 / Math.PI) - 90f;
        m.setYRot(yaw);
        m.setYBodyRot(yaw);
        m.setYHeadRot(yaw);
        if (t % 2 == 0) f.groundRing(m.getBbWidth() * 0.5, 4);
        for (LivingEntity e : f.victims(0.6)) {
            if (hit.add(e) && f.hurt(e, (float) (f.attackDamage() * damageMul))) {
                f.push(e, throwStrength, 0.45);
                f.sound(SoundEvents.GOAT_RAM_IMPACT, 1.5f, 0.8f);
            }
        }
        if (m.horizontalCollision && t > windup + 2) {
            if (breaksBlocks && smash(f)) return;
            f.sound(SoundEvents.RAVAGER_STUNNED, 2f, 0.8f);
            f.groundRing(m.getBbWidth(), 16);
            f.stun(stunTicks);
        }
    }

    /** Breaks the soft blocks in front of the boss. @return true if it broke through (keeps charging) */
    private boolean smash(BossFight f) {
        Mob m = f.mob();
        if (!f.level().getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) return false;
        double w = m.getBbWidth() * 0.5 + 0.6;
        Vec3 c = m.position().add(dir.scale(w));
        boolean hard = false, broke = false;
        int r = (int) Math.ceil(m.getBbWidth() * 0.5);
        for (int dy = 0; dy < Math.ceil(m.getBbHeight()); dy++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    BlockPos p = BlockPos.containing(c.x + dx, m.getY() + dy + 0.1, c.z + dz);
                    BlockState st = f.level().getBlockState(p);
                    if (st.isAir() || st.getCollisionShape(f.level(), p).isEmpty()) continue;
                    float hardness = st.getDestroySpeed(f.level(), p);
                    if (hardness >= 0 && hardness < 1.0f && !st.hasBlockEntity()) {
                        f.level().destroyBlock(p, true, m);
                        broke = true;
                    } else {
                        hard = true;
                    }
                }
            }
        }
        return broke && !hard;
    }
}
