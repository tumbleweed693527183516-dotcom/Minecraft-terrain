package com.vividlands.ragnarok.boss;

import com.vividlands.ragnarok.boss.ability.Ability;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** The running fight of one boss (server side): target, boss bar, abilities, enrage, minions. */
public final class BossFight {
    private static final UUID ENRAGE_SPEED = UUID.fromString("6a4f3c5e-8d1b-4b7a-9c2e-1f0a5b6c7d81");
    private static final UUID ENRAGE_DAMAGE = UUID.fromString("6a4f3c5e-8d1b-4b7a-9c2e-1f0a5b6c7d82");
    public static final double BAR_RANGE = 48, AGGRO_RANGE = 40;

    private final Mob mob;
    private final BossDef def;
    private final ServerBossEvent bar;
    private final List<Ability> abilities = new ArrayList<>();
    private final Map<Ability, Integer> cooldowns = new HashMap<>();
    private final Set<UUID> fighters = new HashSet<>();
    final List<Mob> minions = new ArrayList<>();
    private Ability active;
    private int activeTicks, activeDuration, globalCooldown = 60, idle, stun;
    private boolean enraged;
    private float damageTaken;          // total damage taken (abilities use it to tell whether the player fought back)
    private LivingEntity target;

    BossFight(Mob mob, BossDef def) {
        this.mob = mob;
        this.def = def;
        this.bar = new ServerBossEvent(Component.translatable(def.nameKey()), def.color, BossEvent.BossBarOverlay.NOTCHED_10);
        for (var s : def.abilities) abilities.add(s.get());
        for (Ability a : abilities) cooldowns.put(a, 40 + mob.getRandom().nextInt(60));   // first moves after 2-5 s
        enraged = mob.getHealth() <= mob.getMaxHealth() * 0.5f;
        if (enraged) applyEnrage(false);
    }

    public Mob mob() { return mob; }
    public BossDef def() { return def; }
    public ServerLevel level() { return (ServerLevel) mob.level(); }
    public boolean enraged() { return enraged; }
    public boolean busy() { return active != null || stun > 0; }
    public float damageTaken() { return damageTaken; }
    public LivingEntity target() { return target; }
    Set<UUID> fighters() { return fighters; }

    /** Cooldowns run faster once enraged. */
    private int scaled(int ticks) {
        return enraged ? (int) (ticks * 0.65f) : ticks;
    }

    // ------------------------------------------------------------------ tick
    void tick() {
        if (!mob.isAlive()) return;
        int age = mob.tickCount;
        if (age % 5 == 0) updateBar();
        if (age % 10 == 0) updateTarget();
        if (age % 20 == 0) {
            Compat.keepAwake(mob);
            Bosses.applyStats(mob, def);
        }
        bar.setProgress(Math.max(0f, mob.getHealth() / mob.getMaxHealth()));

        if (target == null) {
            if (++idle > 600 && mob.getHealth() < mob.getMaxHealth()) {    // nobody fought it for 30 s: back to full
                mob.setHealth(mob.getMaxHealth());
                fighters.clear();
            }
        } else {
            idle = 0;
        }
        if (!enraged && mob.getHealth() <= mob.getMaxHealth() * 0.5f) {
            enraged = true;
            Bosses.debug("{} enraged", def.id);
            applyEnrage(true);
        }
        minions.removeIf(m -> !m.isAlive());

        if (stun > 0) {
            stun--;
            freeze();
            if (age % 4 == 0) particles(ParticleTypes.CRIT, mob.getX(), mob.getY() + mob.getBbHeight() + 0.3, mob.getZ(), 3, 0.4, 0.1, 0.4, 0.05);
            return;
        }
        for (Ability a : abilities) {
            if (a.passive()) a.passiveTick(this, target);
        }
        if (active != null) {
            if (target == null || !target.isAlive()) {
                active.end(this);
                active = null;
            } else {
                active.tick(this, target, activeTicks++);
                if (activeTicks >= activeDuration && active != null) {
                    active.end(this);
                    active = null;
                    globalCooldown = scaled(30);
                }
            }
            return;
        }
        cooldowns.replaceAll((a, c) -> c - 1);
        if (--globalCooldown > 0 || target == null) return;
        List<Ability> ready = new ArrayList<>();
        for (Ability a : abilities) {
            if (!a.passive() && cooldowns.getOrDefault(a, 40) <= 0 && a.canStart(this, target)) ready.add(a);
        }
        if (ready.isEmpty()) return;
        Ability pick = ready.get(mob.getRandom().nextInt(ready.size()));
        active = pick;
        activeTicks = 0;
        activeDuration = Math.max(1, pick.start(this, target));
        Bosses.debug("{} uses {} on {} ({} ticks)", def.id, pick.getClass().getSimpleName(),
                target.getType().getDescriptionId(), activeDuration);
        cooldowns.put(pick, scaled(pick.cooldown()));
    }

    /** Ends the running ability now (e.g. a charge that hit something). */
    public void finish() {
        if (active != null) {
            activeDuration = activeTicks;
        }
    }

    public void stun(int ticks) {
        stun = ticks;
        if (active != null) {
            active.end(this);
            active = null;
        }
        mob.getNavigation().stop();
    }

    void onDamaged(float amount, Entity attacker) {
        damageTaken += amount;
        if (attacker instanceof Player p) fighters.add(p.getUUID());
    }

    private void applyEnrage(boolean announce) {
        AttributeInstance speed = mob.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null && speed.getModifier(ENRAGE_SPEED) == null) {
            speed.addTransientModifier(new AttributeModifier(ENRAGE_SPEED, "boss enrage", 0.3, AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
        AttributeInstance dmg = mob.getAttribute(Attributes.ATTACK_DAMAGE);
        if (dmg != null && dmg.getModifier(ENRAGE_DAMAGE) == null) {
            dmg.addTransientModifier(new AttributeModifier(ENRAGE_DAMAGE, "boss enrage", 0.25, AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
        if (announce) {
            mob.playAmbientSound();
            sound(net.minecraft.sounds.SoundEvents.RAVAGER_ROAR, 2f, 0.7f);
            particles(ParticleTypes.ANGRY_VILLAGER, mob.getX(), mob.getY() + mob.getBbHeight(), mob.getZ(), 12, mob.getBbWidth() * 0.6, 0.5, mob.getBbWidth() * 0.6, 0.1);
            for (ServerPlayer p : bar.getPlayers()) {
                p.displayClientMessage(Component.translatable("boss.vividlands_ragnarok.enraged", Component.translatable(def.nameKey())), true);
            }
        }
    }

    // ------------------------------------------------------------------ boss bar and target
    private void updateBar() {
        for (ServerPlayer p : new ArrayList<>(bar.getPlayers())) {
            if (p.isRemoved() || p.level() != mob.level() || p.distanceTo(mob) > BAR_RANGE * 1.25) bar.removePlayer(p);
        }
        for (ServerPlayer p : level().players()) {
            if (p.distanceTo(mob) <= BAR_RANGE && !bar.getPlayers().contains(p)) bar.addPlayer(p);
        }
    }

    void close() {
        bar.removeAllPlayers();
        for (Mob m : minions) m.discard();
        minions.clear();
    }

    private static boolean fightable(LivingEntity e) {
        return e != null && e.isAlive() && !(e instanceof Player p && (p.isCreative() || p.isSpectator()));
    }

    private void updateTarget() {
        LivingEntity t = mob.getTarget();
        if (!fightable(t) || t.distanceTo(mob) > AGGRO_RANGE * 1.5 || Bosses.isBoss(t) || Bosses.isMinion(t)) t = null;
        if (t == null || !(t instanceof Player)) {
            Player nearest = level().getNearestPlayer(mob.getX(), mob.getY(), mob.getZ(), AGGRO_RANGE,
                    e -> e instanceof Player p && fightable(p));
            if (nearest != null) t = nearest;
        }
        target = t;
        if (mob.getTarget() != t) mob.setTarget(t);
        if (t != null && mob instanceof NeutralMob n) {
            n.setPersistentAngerTarget(t.getUUID());
            n.setRemainingPersistentAngerTime(400);
        }
    }

    // ------------------------------------------------------------------ helpers for abilities
    /** Stand still (between moves, during wind-ups). */
    public void freeze() {
        mob.getNavigation().stop();
        Vec3 v = mob.getDeltaMovement();
        mob.setDeltaMovement(0, v.y, 0);
    }

    public void face(Entity e) {
        mob.getLookControl().setLookAt(e, 60f, 60f);
        double dx = e.getX() - mob.getX(), dz = e.getZ() - mob.getZ();
        float yaw = (float) (Math.atan2(dz, dx) * 180 / Math.PI) - 90f;
        mob.setYRot(yaw);
        mob.setYBodyRot(yaw);
        mob.setYHeadRot(yaw);
    }

    public float attackDamage() {
        return def.damage * (enraged ? 1.25f : 1f);
    }

    /** Damage from the boss itself (counts as a mob attack: armour and shields work). */
    public boolean hurt(LivingEntity e, float amount) {
        if (Bosses.isBoss(e) || Bosses.isMinion(e)) return false;
        return e.hurt(mob.damageSources().mobAttack(mob), amount);
    }

    /** A normal melee hit (the pack's own melee goal). */
    public void meleeHit(LivingEntity t) {
        Bosses.debug("{} melee hit on {}", def.id, t.getType().getDescriptionId());
        mob.swing(InteractionHand.MAIN_HAND);
        Compat.attackAnimation(mob);
        if (hurt(t, attackDamage())) push(t, def.knockback, 0.25);
    }

    /** Pushes an entity away from the boss (horizontal strength, then upward). */
    public void push(Entity e, double strength, double up) {
        Vec3 d = new Vec3(e.getX() - mob.getX(), 0, e.getZ() - mob.getZ());
        d = d.lengthSqr() < 1e-4 ? new Vec3(mob.getRandom().nextDouble() - 0.5, 0, mob.getRandom().nextDouble() - 0.5).normalize() : d.normalize();
        double resist = e instanceof LivingEntity l ? 1 - l.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE) * 0.6 : 1;
        e.setDeltaMovement(e.getDeltaMovement().add(d.x * strength * resist, up * resist, d.z * strength * resist));
        e.hurtMarked = true;
    }

    /** Living things in reach that the boss can hurt (players and other creatures, never bosses or minions). */
    public List<LivingEntity> victims(double radius) {
        AABB box = mob.getBoundingBox().inflate(radius, 2, radius);
        return level().getEntitiesOfClass(LivingEntity.class, box, e -> e != mob && fightable(e) && !Bosses.isBoss(e)
                && !Bosses.isMinion(e) && horizontalDistance(e) <= radius + mob.getBbWidth() * 0.5);
    }

    public double horizontalDistance(Entity e) {
        double dx = e.getX() - mob.getX(), dz = e.getZ() - mob.getZ();
        return Math.sqrt(dx * dx + dz * dz);
    }

    /** Distance between the boss's edge and the target's edge. */
    public double gap(Entity e) {
        return Math.max(0, horizontalDistance(e) - mob.getBbWidth() * 0.5 - e.getBbWidth() * 0.5);
    }

    public void sound(SoundEvent s, float volume, float pitch) {
        level().playSound(null, mob.getX(), mob.getY(), mob.getZ(), s, SoundSource.HOSTILE, volume, pitch);
    }

    public void particles(ParticleOptions p, double x, double y, double z, int n, double dx, double dy, double dz, double speed) {
        level().sendParticles(p, x, y, z, n, dx, dy, dz, speed);
    }

    /** Dust of the ground block in a ring around the boss (slams, quakes). */
    public void groundRing(double radius, int points) {
        BlockPos below = mob.blockPosition().below();
        BlockState ground = level().getBlockState(below);
        if (ground.isAir()) ground = net.minecraft.world.level.block.Blocks.DIRT.defaultBlockState();
        BlockParticleOption dust = new BlockParticleOption(ParticleTypes.BLOCK, ground);
        for (int i = 0; i < points; i++) {
            double a = Math.PI * 2 * i / points;
            particles(dust, mob.getX() + Math.cos(a) * radius, mob.getY() + 0.1, mob.getZ() + Math.sin(a) * radius, 3, 0.2, 0.1, 0.2, 0.15);
        }
    }

    public void effect(LivingEntity e, MobEffectInstance inst) {
        if (!Bosses.isBoss(e)) e.addEffect(inst, mob);
    }

    public static MobEffectInstance stunEffect(int ticks) {
        return new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, ticks, 4, false, true, true);
    }

    public boolean inWater() {
        return mob.isInWater() || mob.isUnderWater();
    }
}
