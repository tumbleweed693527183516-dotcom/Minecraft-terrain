package com.vividlands.ragnarok.classes;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.vividlands.ragnarok.Ragnarok;
import com.vividlands.ragnarok.boss.BossDef;
import com.vividlands.ragnarok.boss.Bosses;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.PacketByteBufs;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.Registry;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * The class system: XP and levels, the four abilities of each class, passives, and syncing to the client HUD.
 * Abilities are cast with keys (client/ClassClient) or "/ragnarok class cast <1-4>".
 */
public final class Classes {
    private Classes() {
    }

    public static final ResourceLocation CAST = new ResourceLocation(Ragnarok.MOD_ID, "class_cast");
    public static final ResourceLocation SYNC = new ResourceLocation(Ragnarok.MOD_ID, "class_sync");
    public static final Map<NorseClass, Item> RUNES = new EnumMap<>(NorseClass.class);

    public static ClassData data(Player p) {
        return ((ClassHolder) p).vlr$classes();
    }

    // ------------------------------------------------------------------ timers and effects in the world
    private record Delayed(long at, Runnable run) {
    }

    private record Mark(UUID owner, long until, double everyone, double ownerArrows, boolean healOnKill) {
    }

    private record Trap(ServerLevel level, Vec3 pos, UUID owner, long until, float damage) {
    }

    private record Summon(Wolf wolf, long until) {
    }

    private static final List<Delayed> DELAYED = new ArrayList<>();
    private static final Map<UUID, Mark> MARKS = new HashMap<>();
    private static final List<Trap> TRAPS = new ArrayList<>();
    private static final List<Summon> WOLVES = new ArrayList<>();
    private static final Map<UUID, Long> BLOODRAGE = new HashMap<>(), HUNGER = new HashMap<>();
    private static long now;

    private static void later(int ticks, Runnable r) {
        DELAYED.add(new Delayed(now + ticks, r));
    }

    // ------------------------------------------------------------------ helpers
    private static int lvl(ServerPlayer p) {
        return data(p).level();
    }

    private static double L(ServerPlayer p, double atOne, double atMax) {
        return NorseClass.lerp(lvl(p), atOne, atMax);
    }

    private static boolean hostile(Entity e, Player p) {
        if (e == p || !(e instanceof LivingEntity le) || !le.isAlive() || e instanceof Player || e instanceof ArmorStand) return false;
        if (e instanceof TamableAnimal t && t.isTame()) return false;
        return e instanceof Enemy || Bosses.isBoss(e) || (e instanceof Mob m && m.getTarget() == p);
    }

    private static List<LivingEntity> enemies(ServerPlayer p, Vec3 c, double r) {
        return p.serverLevel().getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(r), e -> hostile(e, p) && e.position().distanceTo(c) <= r);
    }

    private static List<ServerPlayer> allies(ServerPlayer p, double r) {
        return p.serverLevel().getEntitiesOfClass(ServerPlayer.class, p.getBoundingBox().inflate(r), Entity::isAlive);
    }

    private static void particles(ServerPlayer p, ParticleOptions type, Vec3 at, int n, double spread, double speed) {
        p.serverLevel().sendParticles(type, at.x, at.y, at.z, n, spread, spread, spread, speed);
    }

    private static void sound(ServerPlayer p, SoundEvent s, float vol, float pitch) {
        p.serverLevel().playSound(null, p.getX(), p.getY(), p.getZ(), s, SoundSource.PLAYERS, vol, pitch);
    }

    private static void push(ServerPlayer p, Vec3 v) {
        p.setDeltaMovement(v);
        p.connection.send(new ClientboundSetEntityMotionPacket(p));
    }

    private static void effect(LivingEntity e, MobEffect eff, int ticks, int amp) {
        e.addEffect(new MobEffectInstance(eff, ticks, amp, false, true, true));
    }

    private static DamageSource hit(ServerPlayer p) {
        return p.damageSources().playerAttack(p);
    }

    private static Entity lookTarget(ServerPlayer p, double range) {
        Vec3 eye = p.getEyePosition(), end = eye.add(p.getLookAngle().scale(range));
        EntityHitResult r = ProjectileUtil.getEntityHitResult(p.level(), p, eye, end,
                p.getBoundingBox().expandTowards(p.getLookAngle().scale(range)).inflate(1), e -> hostile(e, p));
        if (r == null) return null;
        // stop at walls
        var block = p.level().clip(new net.minecraft.world.level.ClipContext(eye, r.getLocation(),
                net.minecraft.world.level.ClipContext.Block.COLLIDER, net.minecraft.world.level.ClipContext.Fluid.NONE, p));
        if (block.getType() != net.minecraft.world.phys.HitResult.Type.MISS && block.getLocation().distanceTo(eye) < r.getLocation().distanceTo(eye) - 0.5) return null;
        return r.getEntity();
    }

    private static Vec3 lookPoint(ServerPlayer p, double range) {
        Vec3 eye = p.getEyePosition(), end = eye.add(p.getLookAngle().scale(range));
        return p.level().clip(new net.minecraft.world.level.ClipContext(eye, end, net.minecraft.world.level.ClipContext.Block.COLLIDER,
                net.minecraft.world.level.ClipContext.Fluid.NONE, p)).getLocation();
    }

    // ------------------------------------------------------------------ casting
    public static int cooldownTicks(ServerPlayer p, int slot) {
        ClassData d = data(p);
        int level = d.level();
        double t = d.active.abilities.get(slot).cooldownSeconds() * 20 * NorseClass.lerp(level, 1.0, 0.6);
        if (d.active == NorseClass.VOLVA) t *= 1 - 0.005 * level;
        return (int) Math.round(t);
    }

    public static void cast(ServerPlayer p, int slot) {
        ClassData d = data(p);
        if (d.active == null || slot < 0 || slot > 3 || !p.isAlive() || p.isSpectator()) return;
        NorseClass.Ability a = d.active.abilities.get(slot);
        long t = p.level().getGameTime();
        if (d.level() < a.unlock()) {
            p.displayClientMessage(Component.literal(a.name() + " unlocks at " + d.active.title + " level " + a.unlock()).withStyle(ChatFormatting.RED), true);
            return;
        }
        if (d.active == NorseClass.BERSERKER && slot == 3) {
            p.displayClientMessage(Component.literal("Undying Rage is passive: it saves you from a killing blow").withStyle(ChatFormatting.GOLD), true);
            return;
        }
        if (t < d.readyAt[slot]) return;
        boolean done = switch (d.active) {
            case BERSERKER -> berserker(p, slot);
            case VALKYRIE -> valkyrie(p, slot);
            case HUNTSMAN -> huntsman(p, slot);
            case VOLVA -> volva(p, slot);
            case ULFHEDNAR -> ulfhednar(p, slot);
        };
        if (done) {
            com.vividlands.ragnarok.quest.QuestHooks.award(p, "class/" + d.active.id + "_ability_" + (slot + 1));
            d.readyAt[slot] = t + cooldownTicks(p, slot);
            sync(p);
        }
    }

    private static final DustParticleOptions RED = new DustParticleOptions(new Vector3f(0.8f, 0.1f, 0.1f), 1.4f),
            GOLD = new DustParticleOptions(new Vector3f(1f, 0.82f, 0.35f), 1.2f),
            FROST = new DustParticleOptions(new Vector3f(0.7f, 0.9f, 1f), 1.2f),
            RUNE = new DustParticleOptions(new Vector3f(0.65f, 0.4f, 0.95f), 1.2f);

    private static boolean berserker(ServerPlayer p, int slot) {
        switch (slot) {
            case 0 -> {                                  // Bloodrage
                int ticks = (int) (L(p, 6, 11) * 20);
                BLOODRAGE.put(p.getUUID(), now + ticks);
                effect(p, MobEffects.DAMAGE_BOOST, ticks, lvl(p) >= 25 ? 1 : 0);
                sound(p, SoundEvents.RAVAGER_ROAR, 0.8f, 1.4f);
                particles(p, RED, p.position().add(0, 1, 0), 30, 0.6, 0);
            }
            case 1 -> {                                  // Cleaving Leap
                Vec3 look = p.getLookAngle();
                push(p, new Vec3(look.x * 1.3, 0.75, look.z * 1.3));
                sound(p, SoundEvents.PLAYER_ATTACK_SWEEP, 1f, 0.6f);
                float dmg = (float) L(p, 6, 21);
                later(14, () -> {
                    if (!p.isAlive()) return;
                    p.fallDistance = 0;
                    for (LivingEntity e : enemies(p, p.position(), 4)) {
                        e.hurt(hit(p), dmg);
                        Vec3 away = e.position().subtract(p.position()).normalize();
                        e.knockback(0.8, -away.x, -away.z);
                    }
                    particles(p, ParticleTypes.EXPLOSION, p.position(), 6, 1.5, 0);
                    sound(p, SoundEvents.GENERIC_EXPLODE, 0.7f, 1.2f);
                });
            }
            case 2 -> {                                  // Bear Shirt
                effect(p, MobEffects.ABSORPTION, 240, (int) Math.round(L(p, 1, 6)));
                effect(p, MobEffects.DAMAGE_RESISTANCE, 240, 0);
                sound(p, SoundEvents.POLAR_BEAR_WARNING, 1f, 0.8f);
                particles(p, ParticleTypes.CLOUD, p.position().add(0, 1, 0), 20, 0.5, 0.02);
            }
            default -> {
                return false;
            }
        }
        return true;
    }

    private static boolean valkyrie(ServerPlayer p, int slot) {
        switch (slot) {
            case 0 -> {                                  // Spear of the Slain
                Vec3 eye = p.getEyePosition(), look = p.getLookAngle();
                Entity target = lookTarget(p, 24);
                Vec3 end = target != null ? target.position().add(0, target.getBbHeight() / 2, 0) : lookPoint(p, 24);
                double len = end.distanceTo(eye);
                for (double s = 0; s < len; s += 0.6) particles(p, GOLD, eye.add(look.scale(s)), 1, 0.02, 0);
                if (target != null) {
                    target.hurt(hit(p), (float) L(p, 5, 20));
                    particles(p, ParticleTypes.CRIT, end, 12, 0.3, 0.2);
                }
                sound(p, SoundEvents.TRIDENT_THROW, 1f, 1.2f);
            }
            case 1 -> {                                  // Ascent
                push(p, new Vec3(p.getDeltaMovement().x, 1.35, p.getDeltaMovement().z));
                effect(p, MobEffects.SLOW_FALLING, 160, 0);
                particles(p, ParticleTypes.CLOUD, p.position(), 20, 0.4, 0.05);
                sound(p, SoundEvents.ENDER_DRAGON_FLAP, 0.8f, 1.4f);
            }
            case 2 -> {                                  // Freyja's Aegis
                int amp = (int) Math.round(L(p, 1, 5));
                for (ServerPlayer a : allies(p, 10)) {
                    effect(a, MobEffects.ABSORPTION, 300, amp);
                    a.removeEffect(MobEffects.POISON);
                    a.removeEffect(MobEffects.WITHER);
                    particles(p, GOLD, a.position().add(0, 0.1, 0), 14, 0.7, 0);
                }
                sound(p, SoundEvents.BEACON_ACTIVATE, 0.8f, 1.6f);
            }
            case 3 -> {                                  // Choose the Slain
                Entity target = lookTarget(p, 24);
                if (target == null) return false;
                MARKS.put(target.getUUID(), new Mark(p.getUUID(), now + 200, L(p, 0.25, 0.5), 0, true));
                effect((LivingEntity) target, MobEffects.GLOWING, 200, 0);
                sound(p, SoundEvents.WITHER_SPAWN, 0.4f, 1.8f);
                particles(p, GOLD, target.position().add(0, target.getBbHeight() + 0.5, 0), 25, 0.3, 0);
            }
            default -> {
                return false;
            }
        }
        return true;
    }

    private static boolean huntsman(ServerPlayer p, int slot) {
        switch (slot) {
            case 0 -> {                                  // Volley
                int n = (int) Math.round(L(p, 3, 8));
                for (int i = 0; i < n; i++) {
                    float yaw = p.getYRot() + (i - (n - 1) / 2f) * 6f;
                    Arrow arrow = new Arrow(p.level(), p);
                    arrow.shootFromRotation(p, p.getXRot(), yaw, 0, 3.0f, 1.0f);
                    arrow.setBaseDamage(L(p, 2, 4));
                    arrow.pickup = AbstractArrow.Pickup.CREATIVE_ONLY;
                    p.level().addFreshEntity(arrow);
                }
                sound(p, SoundEvents.ARROW_SHOOT, 1f, 0.9f);
            }
            case 1 -> {                                  // Frost Snare
                TRAPS.add(new Trap(p.serverLevel(), p.position(), p.getUUID(), now + 600, (float) L(p, 4, 14)));
                particles(p, FROST, p.position().add(0, 0.2, 0), 25, 0.6, 0);
                sound(p, SoundEvents.CHAIN_PLACE, 1f, 0.7f);
            }
            case 2 -> {                                  // Hunter's Mark
                double bonus = L(p, 0.10, 0.25);
                for (LivingEntity e : enemies(p, p.position(), 32)) {
                    MARKS.merge(e.getUUID(), new Mark(p.getUUID(), now + 200, 0, bonus, false), (a, b) -> a.everyone() > 0 ? a : b);
                    effect(e, MobEffects.GLOWING, 200, 0);
                }
                sound(p, SoundEvents.SPYGLASS_USE, 1f, 0.8f);
            }
            case 3 -> {                                  // Skadi's Hailstorm
                Vec3 at = lookPoint(p, 40);
                double dmg = L(p, 3, 6);
                for (int w = 0; w < 25; w++) {
                    later(w * 4, () -> {
                        for (int k = 0; k < 2; k++) {
                            Arrow arrow = new Arrow(p.level(), p);
                            double ox = (p.getRandom().nextDouble() - 0.5) * 8, oz = (p.getRandom().nextDouble() - 0.5) * 8;
                            arrow.setPos(at.x + ox, at.y + 14, at.z + oz);
                            arrow.setDeltaMovement(0, -2.2, 0);
                            arrow.setBaseDamage(dmg);
                            arrow.pickup = AbstractArrow.Pickup.CREATIVE_ONLY;
                            p.level().addFreshEntity(arrow);
                        }
                    });
                }
                particles(p, FROST, at.add(0, 1, 0), 40, 3, 0);
                sound(p, SoundEvents.ARROW_SHOOT, 1f, 0.5f);
            }
            default -> {
                return false;
            }
        }
        return true;
    }

    private static boolean volva(ServerPlayer p, int slot) {
        switch (slot) {
            case 0 -> {                                  // Kenaz: rune fire bolt
                Vec3 eye = p.getEyePosition(), look = p.getLookAngle();
                Entity target = lookTarget(p, 28);
                Vec3 end = target != null ? target.position().add(0, target.getBbHeight() / 2, 0) : lookPoint(p, 28);
                for (double s = 0; s < end.distanceTo(eye); s += 0.5) particles(p, ParticleTypes.FLAME, eye.add(look.scale(s)), 1, 0.03, 0.005);
                if (target != null) {
                    target.hurt(p.damageSources().indirectMagic(p, p), (float) L(p, 4, 16));
                    target.setSecondsOnFire(4);
                }
                sound(p, SoundEvents.BLAZE_SHOOT, 0.8f, 1.3f);
            }
            case 1 -> {                                  // Isa: cone of frost
                Vec3 look = p.getLookAngle();
                float dmg = (float) L(p, 3, 13);
                for (LivingEntity e : enemies(p, p.position(), 8)) {
                    Vec3 to = e.position().subtract(p.position()).normalize();
                    if (to.dot(look) < 0.6) continue;
                    e.hurt(p.damageSources().indirectMagic(p, p), dmg);
                    effect(e, MobEffects.MOVEMENT_SLOWDOWN, 100, 2);
                    e.setTicksFrozen(Math.max(e.getTicksFrozen(), 140));
                }
                for (int i = 1; i < 8; i++) particles(p, ParticleTypes.SNOWFLAKE, p.getEyePosition().add(look.scale(i)), 6, 0.2 * i / 2, 0.01);
                sound(p, SoundEvents.GLASS_BREAK, 1f, 0.6f);
            }
            case 2 -> {                                  // Algiz: ward
                int ticks = (int) (L(p, 5, 10) * 20);
                for (ServerPlayer a : allies(p, 8)) {
                    effect(a, MobEffects.REGENERATION, ticks, 1);
                    particles(p, RUNE, a.position().add(0, 0.1, 0), 14, 0.7, 0);
                }
                sound(p, SoundEvents.AMETHYST_BLOCK_CHIME, 1.5f, 0.8f);
            }
            case 3 -> {                                  // Thurisaz: lightning
                int n = (int) Math.round(L(p, 3, 8));
                float dmg = (float) L(p, 8, 28);
                List<LivingEntity> list = enemies(p, p.position(), 16);
                list.sort((a, b) -> Double.compare(a.distanceToSqr(p), b.distanceToSqr(p)));
                if (list.isEmpty()) return false;
                for (LivingEntity e : list.subList(0, Math.min(n, list.size()))) {
                    LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(p.level());
                    if (bolt != null) {
                        bolt.moveTo(e.position());
                        bolt.setVisualOnly(true);
                        p.level().addFreshEntity(bolt);
                    }
                    e.hurt(p.damageSources().indirectMagic(p, p), dmg);
                }
            }
            default -> {
                return false;
            }
        }
        return true;
    }

    private static boolean ulfhednar(ServerPlayer p, int slot) {
        switch (slot) {
            case 0 -> {                                  // Call the Pack
                int n = (int) Math.round(L(p, 1, 4));
                for (int i = 0; i < n; i++) {
                    Wolf w = EntityType.WOLF.create(p.level());
                    if (w == null) continue;
                    w.moveTo(p.getX() + (i - n / 2.0), p.getY(), p.getZ() + 1, p.getYRot(), 0);
                    w.tame(p);
                    AttributeInstance hp = w.getAttribute(Attributes.MAX_HEALTH), atk = w.getAttribute(Attributes.ATTACK_DAMAGE);
                    if (hp != null) hp.setBaseValue(L(p, 20, 60));
                    if (atk != null) atk.setBaseValue(L(p, 4, 12));
                    w.setHealth(w.getMaxHealth());
                    w.addTag("vividlands_ragnarok.spirit_wolf");
                    p.level().addFreshEntity(w);
                    WOLVES.add(new Summon(w, now + 600));
                    particles(p, ParticleTypes.SOUL, w.position().add(0, 0.5, 0), 10, 0.3, 0.02);
                }
                sound(p, SoundEvents.WOLF_HOWL, 1f, 1f);
            }
            case 1 -> {                                  // Howl
                int ticks = (int) (L(p, 6, 11) * 20);
                for (LivingEntity e : enemies(p, p.position(), 10)) {
                    effect(e, MobEffects.WEAKNESS, ticks, 0);
                    effect(e, MobEffects.MOVEMENT_SLOWDOWN, ticks, 0);
                }
                for (Summon s : WOLVES) if (s.wolf().getOwner() == p) effect(s.wolf(), MobEffects.DAMAGE_BOOST, ticks, 1);
                sound(p, SoundEvents.WOLF_HOWL, 1.5f, 0.6f);
            }
            case 2 -> {                                  // Wolf Form
                int ticks = (int) (L(p, 14, 24) * 20);
                effect(p, MobEffects.MOVEMENT_SPEED, ticks, 1);
                effect(p, MobEffects.JUMP, ticks, 1);
                effect(p, MobEffects.DAMAGE_BOOST, ticks, 0);
                effect(p, MobEffects.NIGHT_VISION, ticks, 0);
                particles(p, ParticleTypes.LARGE_SMOKE, p.position().add(0, 1, 0), 20, 0.4, 0.02);
                sound(p, SoundEvents.WOLF_GROWL, 1f, 0.7f);
            }
            case 3 -> {                                  // Fenrir's Hunger
                HUNGER.put(p.getUUID(), now + 160);
                sound(p, SoundEvents.WOLF_GROWL, 1.2f, 0.5f);
                particles(p, RED, p.position().add(0, 1, 0), 25, 0.5, 0);
            }
            default -> {
                return false;
            }
        }
        return true;
    }

    // ------------------------------------------------------------------ damage hooks (called from ClassDamageMixin)
    /** Scales damage dealt to {@code target} by class passives, marks and buffs, and applies on-hit effects. */
    public static float outgoing(LivingEntity target, DamageSource source, float amount) {
        if (amount <= 0 || target.level().isClientSide) return amount;
        Entity direct = source.getDirectEntity();
        Entity owner = source.getEntity();
        float out = amount;
        Mark mark = MARKS.get(target.getUUID());
        if (mark != null && mark.until() > now) {
            out *= (float) (1 + mark.everyone());
            if (direct instanceof AbstractArrow && owner != null && owner.getUUID().equals(mark.owner())) out *= (float) (1 + mark.ownerArrows());
        }
        if (!(owner instanceof ServerPlayer p)) return out;
        ClassData d = data(p);
        if (d.active == null) return out;
        int level = d.level();
        boolean melee = direct == p;
        if (d.active == NorseClass.BERSERKER && melee) {
            out *= 1 + 0.01f * level;
            Long until = BLOODRAGE.get(p.getUUID());
            if (until != null && until > now) p.heal((float) (out * NorseClass.lerp(level, 0.10, 0.30)));
        }
        if (d.active == NorseClass.HUNTSMAN && direct instanceof AbstractArrow) out *= 1 + 0.01f * level;
        if (d.active == NorseClass.ULFHEDNAR && melee) {
            Long until = HUNGER.get(p.getUUID());
            if (until != null && until > now) {
                p.heal((float) NorseClass.lerp(level, 2, 4));
                if (Bosses.BLEEDING != null) target.addEffect(new MobEffectInstance(Bosses.BLEEDING, 100, 0), p);
            }
        }
        return out;
    }

    // ------------------------------------------------------------------ XP
    public static void giveXp(ServerPlayer p, int amount) {
        ClassData d = data(p);
        if (d.active == null || amount <= 0) return;
        int before = d.level();
        d.xp.merge(d.active, amount, Integer::sum);
        int after = d.level();
        com.vividlands.ragnarok.quest.QuestHooks.classLevels(p, d);
        if (after > before) {
            sound(p, SoundEvents.PLAYER_LEVELUP, 0.8f, 0.8f);
            FriendlyByteBuf t = PacketByteBufs.create();
            t.writeVarInt(2);
            t.writeVarInt(d.active.ordinal());
            t.writeVarInt(after);
            String unlocked = "";
            for (NorseClass.Ability a : d.active.abilities) if (a.unlock() > before && a.unlock() <= after) unlocked = a.name();
            t.writeUtf(unlocked);
            ServerPlayNetworking.send(p, Bosses.POPUP, t);
            applyPassives(p);
        }
        sync(p);
    }

    private static void onKill(LivingEntity dead, DamageSource source) {
        BossDef def = Bosses.defOf(dead);
        Entity killer = source.getEntity();
        if (killer instanceof Wolf w && w.getTags().contains("vividlands_ragnarok.spirit_wolf") && w.getOwner() instanceof ServerPlayer o) killer = o;
        if (def != null) {
            // a boss: everyone near the fight gets the full reward
            for (ServerPlayer p : ((ServerLevel) dead.level()).getEntitiesOfClass(ServerPlayer.class, dead.getBoundingBox().inflate(48), Entity::isAlive)) {
                giveXp(p, def.xpReward());
            }
            return;
        }
        if (killer instanceof ServerPlayer p && !(dead instanceof Player)) {
            giveXp(p, Math.max(1, Math.round(dead.getMaxHealth() / 4)));
        }
        Mark mark = MARKS.remove(dead.getUUID());
        if (mark != null && mark.healOnKill() && dead.level() instanceof ServerLevel sl && sl.getEntity(mark.owner()) instanceof ServerPlayer o) {
            o.heal(12);
        }
    }

    // ------------------------------------------------------------------ passives
    private static final UUID ARMOR = UUID.fromString("a5d0c7e2-1b8f-4c3e-9f2a-7d6b5c4a3e01");
    private static final UUID SPEED = UUID.fromString("a5d0c7e2-1b8f-4c3e-9f2a-7d6b5c4a3e02");

    public static void applyPassives(ServerPlayer p) {
        ClassData d = data(p);
        int level = d.level();
        setMod(p.getAttribute(Attributes.ARMOR), ARMOR, d.active == NorseClass.VALKYRIE ? 0.1 * level : 0, AttributeModifier.Operation.ADDITION);
        setMod(p.getAttribute(Attributes.MOVEMENT_SPEED), SPEED, d.active == NorseClass.ULFHEDNAR ? 0.004 * level : 0, AttributeModifier.Operation.MULTIPLY_BASE);
    }

    private static void setMod(AttributeInstance inst, UUID id, double amount, AttributeModifier.Operation op) {
        if (inst == null) return;
        AttributeModifier cur = inst.getModifier(id);
        if (cur != null && cur.getAmount() == amount) return;
        if (cur != null) inst.removeModifier(id);
        if (amount != 0) inst.addTransientModifier(new AttributeModifier(id, "Vivid Lands class", amount, op));
    }

    public static void setClass(ServerPlayer p, NorseClass c) {
        ClassData d = data(p);
        if (d.active == c) {
            p.displayClientMessage(Component.literal("You already walk the path of the " + c.title).withStyle(ChatFormatting.GRAY), true);
            return;
        }
        d.active = c;
        java.util.Arrays.fill(d.readyAt, 0);
        com.vividlands.ragnarok.quest.QuestHooks.award(p, "class/use_rune");
        com.vividlands.ragnarok.quest.QuestHooks.classLevels(p, d);
        applyPassives(p);
        p.displayClientMessage(Component.literal("You walk the path of the " + c.title + " (level " + d.level(c) + ")")
                .withStyle(s -> s.withColor(c.color)), false);
        sound(p, SoundEvents.ENCHANTMENT_TABLE_USE, 1f, 0.8f);
        sync(p);
    }

    // ------------------------------------------------------------------ sync to the HUD
    public static void sync(ServerPlayer p) {
        ClassData d = data(p);
        FriendlyByteBuf buf = PacketByteBufs.create();
        for (NorseClass c : NorseClass.values()) buf.writeVarInt(d.level(c));
        buf.writeVarInt(d.active == null ? -1 : d.active.ordinal());
        if (d.active != null) {
            int level = d.level();
            buf.writeVarInt(level);
            buf.writeVarInt(d.xpInLevel(d.active));
            buf.writeVarInt(NorseClass.xpToNext(level));
            long t = p.level().getGameTime();
            for (int i = 0; i < 4; i++) {
                long left = d.active == NorseClass.BERSERKER && i == 3 ? d.undyingReadyAt - t : d.readyAt[i] - t;
                buf.writeVarInt((int) Math.max(0, left));
                buf.writeVarInt(cooldownTicks(p, i));
            }
        }
        ServerPlayNetworking.send(p, SYNC, buf);
    }

    // ------------------------------------------------------------------ ticking
    private static void tick(MinecraftServer server) {
        now = server.overworld().getGameTime();
        if (!DELAYED.isEmpty()) {
            List<Delayed> due = new ArrayList<>();
            for (Iterator<Delayed> it = DELAYED.iterator(); it.hasNext(); ) {
                Delayed dl = it.next();
                if (dl.at() <= now) {
                    due.add(dl);
                    it.remove();
                }
            }
            due.forEach(dl -> dl.run().run());
        }
        MARKS.values().removeIf(m -> m.until() <= now);
        for (Iterator<Trap> it = TRAPS.iterator(); it.hasNext(); ) {
            Trap tr = it.next();
            if (tr.until() <= now || !(tr.level().getEntity(tr.owner()) instanceof ServerPlayer owner)) {
                it.remove();
                continue;
            }
            if (now % 10 == 0) tr.level().sendParticles(FROST, tr.pos().x, tr.pos().y + 0.1, tr.pos().z, 3, 0.4, 0, 0.4, 0);
            List<LivingEntity> caught = enemies(owner, tr.pos(), 1.8);
            if (!caught.isEmpty()) {
                for (LivingEntity e : caught) {
                    e.hurt(hit(owner), tr.damage());
                    effect(e, MobEffects.MOVEMENT_SLOWDOWN, 80, 5);
                    e.setTicksFrozen(200);
                }
                tr.level().sendParticles(ParticleTypes.SNOWFLAKE, tr.pos().x, tr.pos().y + 0.5, tr.pos().z, 40, 0.8, 0.5, 0.8, 0.02);
                tr.level().playSound(null, tr.pos().x, tr.pos().y, tr.pos().z, SoundEvents.GLASS_BREAK, SoundSource.PLAYERS, 1f, 0.5f);
                it.remove();
            }
        }
        for (Iterator<Summon> it = WOLVES.iterator(); it.hasNext(); ) {
            Summon s = it.next();
            if (s.until() <= now || !s.wolf().isAlive()) {
                if (s.wolf().isAlive() && s.wolf().level() instanceof ServerLevel sl) {
                    sl.sendParticles(ParticleTypes.SOUL, s.wolf().getX(), s.wolf().getY() + 0.5, s.wolf().getZ(), 10, 0.3, 0.3, 0.3, 0.02);
                }
                s.wolf().discard();
                it.remove();
            }
        }
        if (now % 10 == 0) {
            for (ServerPlayer p : server.getPlayerList().getPlayers()) {
                if (data(p).active != null) sync(p);
                if (now % 40 == 0) applyPassives(p);
            }
        }
    }

    // ------------------------------------------------------------------ setup
    public static void register() {
        for (NorseClass c : NorseClass.values()) {
            RUNES.put(c, Registry.register(BuiltInRegistries.ITEM, new ResourceLocation(Ragnarok.MOD_ID, c.id + "_rune"),
                    new RuneStoneItem(c, new Item.Properties().stacksTo(1))));
        }
        ServerPlayNetworking.registerGlobalReceiver(CAST, (server, player, handler, buf, sender) -> {
            int slot = buf.readVarInt();
            server.execute(() -> cast(player, slot));
        });
        ServerTickEvents.END_SERVER_TICK.register(Classes::tick);
        ServerLivingEntityEvents.AFTER_DEATH.register(Classes::onKill);
        ServerLivingEntityEvents.ALLOW_DAMAGE.register((entity, source, amount) ->
                !(entity instanceof ServerPlayer p && data(p).active == NorseClass.VALKYRIE && source.is(net.minecraft.tags.DamageTypeTags.IS_FALL)));
        ServerLivingEntityEvents.ALLOW_DEATH.register((entity, source, amount) -> {
            if (!(entity instanceof ServerPlayer p)) return true;
            ClassData d = data(p);
            if (d.active != NorseClass.BERSERKER || d.level() < 35 || p.level().getGameTime() < d.undyingReadyAt) return true;
            d.undyingReadyAt = p.level().getGameTime() + (long) (NorseClass.lerp(d.level(), 300, 180) * 20);
            p.setHealth(1);
            effect(p, MobEffects.DAMAGE_RESISTANCE, 60, 4);
            effect(p, MobEffects.REGENERATION, 100, 2);
            effect(p, MobEffects.DAMAGE_BOOST, 200, 1);
            sound(p, SoundEvents.TOTEM_USE, 1f, 0.7f);
            particles(p, RED, p.position().add(0, 1, 0), 40, 0.6, 0);
            p.displayClientMessage(Component.literal("Undying Rage!").withStyle(ChatFormatting.DARK_RED), true);
            com.vividlands.ragnarok.quest.QuestHooks.award(p, "class/berserker_ability_4");
            return false;
        });
        ServerPlayerEvents.COPY_FROM.register((oldP, newP, alive) -> data(newP).copyFrom(data(oldP)));
        ServerPlayerEvents.AFTER_RESPAWN.register((oldP, newP, alive) -> {
            applyPassives(newP);
            sync(newP);
        });
        CommandRegistrationCallback.EVENT.register((dispatcher, ctx, env) -> dispatcher.register(Commands.literal("ragnarok")
                .then(Commands.literal("class")
                        .then(Commands.literal("cast").then(Commands.argument("slot", IntegerArgumentType.integer(1, 4))
                                .executes(c -> {
                                    cast(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "slot") - 1);
                                    return 1;
                                })))
                        .then(Commands.literal("set").requires(s -> s.hasPermission(2))
                                .then(Commands.argument("class", StringArgumentType.word())
                                        .then(Commands.argument("level", IntegerArgumentType.integer(1, NorseClass.MAX_LEVEL))
                                                .executes(c -> {
                                                    ServerPlayer p = c.getSource().getPlayerOrException();
                                                    NorseClass nc = NorseClass.byId(StringArgumentType.getString(c, "class"));
                                                    if (nc == null) return 0;
                                                    data(p).setLevel(nc, IntegerArgumentType.getInteger(c, "level"));
                                                    data(p).active = null;
                                                    setClass(p, nc);
                                                    return 1;
                                                }))))
                        .then(Commands.literal("xp").requires(s -> s.hasPermission(2))
                                .then(Commands.argument("amount", IntegerArgumentType.integer(1)).executes(c -> {
                                    giveXp(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "amount"));
                                    return 1;
                                })))
                        .then(Commands.literal("ready").requires(s -> s.hasPermission(2)).executes(c -> {
                            ServerPlayer p = c.getSource().getPlayerOrException();
                            java.util.Arrays.fill(data(p).readyAt, 0);
                            return 1;
                        })))));
    }
}
