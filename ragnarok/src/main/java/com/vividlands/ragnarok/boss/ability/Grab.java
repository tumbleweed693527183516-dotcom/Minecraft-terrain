package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/**
 * Grabs you. SQUEEZE (the anaconda's coils, a bear hug): held in place and crushed; hit the boss hard enough to break
 * free, and it's stunned for a moment. CARRY (the eagle's talons): lifted into the air and dropped; hit it to make
 * it let go early, before it gets too high.
 */
public class Grab extends Ability {
    public enum Mode { SQUEEZE, CARRY }

    private final int hold;
    private final double damageMul, liftHeight;
    private final Mode mode;
    private LivingEntity held;
    private float damageAtGrab;
    private double startY;

    public Grab(int cooldown, int hold, double damageMul, Mode mode, double liftHeight) {
        super(cooldown);
        this.hold = hold;
        this.damageMul = damageMul;
        this.mode = mode;
        this.liftHeight = liftHeight;
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return f.gap(target) <= f.def().reach() + 1.5 && !target.isPassenger();
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        held = null;
        f.sound(SoundEvents.RAVAGER_ATTACK, 1.5f, 0.8f);
        return 10 + hold;
    }

    private Vec3 holdPoint(Mob m) {
        double r = Math.toRadians(m.getYRot());
        Vec3 fwd = new Vec3(-Math.sin(r), 0, Math.cos(r));
        if (mode == Mode.CARRY) return m.position().add(0, -1.6, 0);          // dangling from the talons
        return m.position().add(fwd.scale(m.getBbWidth() * 0.55 + 0.3)).add(0, m.getBbHeight() * 0.25, 0);
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Mob m = f.mob();
        if (t < 10) {                                    // the lunge
            f.face(target);
            f.freeze();
            if (t == 9) {
                if (f.gap(target) > f.def().reach() + 1.0 || !f.hurt(target, (float) (f.attackDamage() * 0.5))) {
                    f.finish();                          // missed
                    return;
                }
                held = target;
                damageAtGrab = f.damageTaken();
                startY = m.getY();
                f.animate("grab");
                if (held instanceof ServerPlayer p) p.displayClientMessage(Component.translatable("boss.vividlands_ragnarok.grabbed"), true);
            }
            return;
        }
        if (held == null || !held.isAlive()) {
            f.finish();
            return;
        }
        // break free: hit it hard while held
        if (f.damageTaken() - damageAtGrab > m.getMaxHealth() * 0.03f) {
            release(f);
            if (mode == Mode.SQUEEZE) f.stun(40);
            f.finish();
            return;
        }
        if (mode == Mode.CARRY) {
            m.getNavigation().stop();
            double up = m.getY() - startY < liftHeight ? 0.25 : 0;
            m.setDeltaMovement(m.getDeltaMovement().x * 0.5, up, m.getDeltaMovement().z * 0.5);
        } else {
            f.freeze();
        }
        Vec3 p = holdPoint(m);
        held.teleportTo(p.x, p.y, p.z);
        held.setDeltaMovement(Vec3.ZERO);
        held.fallDistance = 0;
        f.effect(held, new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 10, 3, false, false));
        if (mode == Mode.SQUEEZE && t % 10 == 0) {
            f.sound(SoundEvents.PLAYER_HURT_SWEET_BERRY_BUSH, 1f, 0.5f);
            f.hurt(held, (float) (f.attackDamage() * damageMul));
        }
        if (t == 10 + hold - 1) {
            if (mode == Mode.CARRY) f.hurt(held, (float) (f.attackDamage() * damageMul));
            release(f);
        }
    }

    private void release(BossFight f) {
        if (held != null) {
            if (mode == Mode.SQUEEZE) f.push(held, 1.0, 0.4);
            held = null;
        }
    }

    @Override
    public void end(BossFight f) {
        release(f);
    }
}
