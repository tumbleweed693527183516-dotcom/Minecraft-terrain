package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * Arena hazard: the boss roars and things fall from the sky (icicles, rocks, fire, lightning). Each impact is
 * marked on the ground first; keep moving and stay out of the circles.
 */
public class HazardRain extends Ability {
    public enum Kind { ICICLE, ROCK, FIRE, LIGHTNING }

    private final int count, delay, waves;
    private final double radius, damageMul, spread;
    private final Kind kind;
    private final List<Vec3> spots = new ArrayList<>();

    public HazardRain(int cooldown, int waves, int count, int delay, double radius, double spread, double damageMul, Kind kind) {
        super(cooldown);
        this.waves = waves;
        this.count = count;
        this.delay = delay;
        this.radius = radius;
        this.spread = spread;
        this.damageMul = damageMul;
        this.kind = kind;
        range(0, 30);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        f.sound(SoundEvents.ENDER_DRAGON_GROWL, 1.5f, 0.8f);
        return 15 + waves * (delay + 6);
    }

    private ParticleOptions fx() {
        return switch (kind) {
            case ICICLE -> new BlockParticleOption(ParticleTypes.BLOCK, Blocks.PACKED_ICE.defaultBlockState());
            case ROCK -> new BlockParticleOption(ParticleTypes.BLOCK, Blocks.COBBLESTONE.defaultBlockState());
            case FIRE -> ParticleTypes.LAVA;
            case LIGHTNING -> ParticleTypes.ELECTRIC_SPARK;
        };
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.freeze();
        f.face(target);
        if (t < 15) return;
        int w = (t - 15) % (delay + 6);
        if (w == 0) {                                    // pick this wave's spots: one on you, the rest around you
            spots.clear();
            spots.add(f.groundAt(target.getX(), target.getY(), target.getZ()));
            for (int i = 1; i < count; i++) {
                double a = f.mob().getRandom().nextDouble() * Math.PI * 2, d = 2 + f.mob().getRandom().nextDouble() * spread;
                spots.add(f.groundAt(target.getX() + Math.cos(a) * d, target.getY(), target.getZ() + Math.sin(a) * d));
            }
        }
        if (w < delay) {
            if (w % 3 == 0) for (Vec3 s : spots) {
                f.marker(s, radius, BossFight.DANGER);
                f.particles(fx(), s.x, s.y + 12 - 12.0 * w / delay, s.z, 2, 0.3, 0.3, 0.3, 0.0);   // falling
            }
            return;
        }
        if (w == delay) {
            for (Vec3 s : spots) {
                f.particles(fx(), s.x, s.y + 0.3, s.z, 30, radius * 0.4, 0.3, radius * 0.4, 0.2);
                if (kind == Kind.LIGHTNING) {
                    LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(f.level());
                    if (bolt != null) {
                        bolt.moveTo(s);
                        bolt.setVisualOnly(true);
                        f.level().addFreshEntity(bolt);
                    }
                }
                for (LivingEntity e : f.level().getEntitiesOfClass(LivingEntity.class,
                        new net.minecraft.world.phys.AABB(s, s).inflate(radius, 3, radius),
                        e -> e != f.mob() && e.position().distanceTo(s) <= radius + 0.5)) {
                    if (f.hurt(e, (float) (f.attackDamage() * damageMul)) && kind == Kind.FIRE) e.setSecondsOnFire(3);
                }
            }
            f.sound(kind == Kind.ICICLE ? SoundEvents.GLASS_BREAK : kind == Kind.FIRE ? SoundEvents.FIRECHARGE_USE
                    : SoundEvents.GENERIC_EXPLODE, 1.5f, 0.8f);
        }
    }
}
