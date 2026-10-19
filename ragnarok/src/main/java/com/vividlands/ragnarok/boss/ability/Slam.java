package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;

import java.util.function.Supplier;

/** Rears up (a small hop) and crashes down: damage and knock-up around it, strongest close in. */
public class Slam extends Ability {
    private final int windup;
    private final double radius, damageMul, knockUp;
    private final Supplier<MobEffectInstance> effect;

    public Slam(int cooldown, int windup, double radius, double damageMul, double knockUp, Supplier<MobEffectInstance> effect) {
        super(cooldown);
        this.windup = windup;
        this.radius = radius;
        this.damageMul = damageMul;
        this.knockUp = knockUp;
        this.effect = effect;
        range(0, radius * 0.8);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        f.mob().setDeltaMovement(0, 0.55, 0);
        f.mob().hurtMarked = true;
        return windup + 10;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.freeze();
        f.face(target);
        if (t == windup) {
            f.sound(SoundEvents.GENERIC_EXPLODE, 1.2f, 0.55f);
            f.sound(SoundEvents.ANVIL_LAND, 0.8f, 0.5f);
            for (int ring = 1; ring <= 3; ring++) f.groundRing(radius * ring / 3, 10 * ring);
            for (LivingEntity e : f.victims(radius)) {
                if (!e.onGround() && e.getY() > f.mob().getY() + 1.5) continue;     // jumped over it
                double near = 1 - Math.min(1, f.horizontalDistance(e) / (radius + f.mob().getBbWidth() * 0.5));
                if (f.hurt(e, (float) (f.attackDamage() * damageMul * (0.5 + 0.5 * near)))) {
                    f.push(e, 0.6 + near, knockUp);
                    if (effect != null) f.effect(e, effect.get());
                }
            }
        }
    }
}
