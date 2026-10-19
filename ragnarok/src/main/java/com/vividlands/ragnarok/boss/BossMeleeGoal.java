package com.vividlands.ragnarok.boss;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;
import java.util.function.Supplier;

/**
 * Chase and hit, for bosses (and minions) built on creatures that don't attack on their own (elk, mammoth...).
 * Runs at the highest priority so the creature's own flee / wander / eat goals can't interrupt the fight.
 * While the boss is using a special move the goal just holds on to movement (the move steers the boss).
 */
final class BossMeleeGoal extends Goal {
    private final Mob mob;
    private final Supplier<BossFight> fight;      // null fight = a minion
    private final float damage, reach;
    private final int interval;
    private int cooldown, repath;

    BossMeleeGoal(Mob mob, Supplier<BossFight> fight, float damage, float reach, int interval) {
        this.mob = mob;
        this.fight = fight;
        this.damage = damage;
        this.reach = reach;
        this.interval = interval;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private static boolean valid(LivingEntity t) {
        return t != null && t.isAlive() && !t.isSpectator() && !(t instanceof net.minecraft.world.entity.player.Player p && p.isCreative());
    }

    @Override
    public boolean canUse() {
        return valid(mob.getTarget());
    }

    @Override
    public boolean canContinueToUse() {
        return valid(mob.getTarget());
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void stop() {
        mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        LivingEntity t = mob.getTarget();
        if (t == null) return;
        BossFight f = fight == null ? null : fight.get();
        if (f != null && f.busy()) return;
        if (cooldown > 0) cooldown--;
        mob.getLookControl().setLookAt(t, 30f, 30f);
        double dx = t.getX() - mob.getX(), dz = t.getZ() - mob.getZ();
        double gap = Math.sqrt(dx * dx + dz * dz) - mob.getBbWidth() * 0.5 - t.getBbWidth() * 0.5;
        double speed = f != null && f.enraged() ? 1.35 : 1.15;
        if (gap > reach - 0.2) {
            if (--repath <= 0) {
                repath = 8 + mob.getRandom().nextInt(5);
                boolean ok = mob.getNavigation().moveTo(t, speed);
                if (!ok || mob.getNavigation().isStuck()) {
                    // big bodies often find no path through trees: just head straight for the target
                    mob.getMoveControl().setWantedPosition(t.getX(), t.getY(), t.getZ(), speed);
                }
            }
        } else {
            mob.getNavigation().stop();
        }
        if (gap <= reach && cooldown <= 0 && mob.hasLineOfSight(t)) {
            cooldown = interval;
            if (f != null) {
                f.meleeHit(t);
            } else {
                mob.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                Compat.attackAnimation(mob);
                t.hurt(mob.damageSources().mobAttack(mob), damage);
            }
        }
    }
}
