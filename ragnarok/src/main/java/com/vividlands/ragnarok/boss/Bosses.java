package com.vividlands.ragnarok.boss;

import com.vividlands.ragnarok.Ragnarok;
import com.vividlands.ragnarok.boss.BossDef.Melee;
import com.vividlands.ragnarok.boss.ability.Capsize;
import com.vividlands.ragnarok.boss.ability.Charge;
import com.vividlands.ragnarok.boss.ability.DeathRoll;
import com.vividlands.ragnarok.boss.ability.Fling;
import com.vividlands.ragnarok.boss.ability.Leap;
import com.vividlands.ragnarok.boss.ability.Maul;
import com.vividlands.ragnarok.boss.ability.Roar;
import com.vividlands.ragnarok.boss.ability.Shockwave;
import com.vividlands.ragnarok.boss.ability.Slam;
import com.vividlands.ragnarok.boss.ability.Stalk;
import com.vividlands.ragnarok.boss.ability.Summon;
import com.vividlands.ragnarok.boss.ability.Throw;
import com.vividlands.ragnarok.mixin.MobGoalsAccessor;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.gamerule.v1.GameRuleFactory;
import net.fabricmc.fabric.api.gamerule.v1.GameRuleRegistry;
import net.fabricmc.fabric.api.networking.v1.EntityTrackingEvents;
import net.fabricmc.fabric.api.networking.v1.PacketByteBufs;
import net.fabricmc.fabric.api.networking.v1.PlayerLookup;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent.BossBarColor;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * The pack's bosses. Each one is a real creature from another mod (Naturalist, Fossils and Archeology,
 * Animal Garden) made into a boss: bigger, much tougher, with a boss bar, special moves, and a trophy when beaten.
 * Nothing of those mods is copied: the creature is spawned as itself and keeps its own model and animations.
 *
 * Chapter 1 (Skadi's hunter's trials) bosses roam their home biomes (one per region), except the Silverback, who
 * guards the Mayan temples. Several only appear once enough other trials are done (see {@link BossDef#after}).
 */
public final class Bosses {
    public static final String TAG = "vividlands_ragnarok.boss.";
    public static final String MINION_TAG = "vividlands_ragnarok.minion";
    public static final ResourceLocation PACKET = new ResourceLocation(Ragnarok.MOD_ID, "boss");
    public static final Map<String, BossDef> DEFS = new LinkedHashMap<>();
    static final Map<Mob, BossFight> FIGHTS = new HashMap<>();
    public static EntityType<Boulder> BOULDER;
    public static MobEffect BLEEDING;
    public static GameRules.Key<GameRules.BooleanValue> SPAWNING;
    private static boolean addingMinion;
    /** -Dvividlands.bossdebug=true: log every boss move (pack test). */
    public static final boolean DEBUG = Boolean.getBoolean("vividlands.bossdebug");

    public static void debug(String msg, Object... args) {
        if (DEBUG) Ragnarok.LOG.info("[boss] " + msg, args);
    }

    private Bosses() {
    }

    private static BossDef def(String id) {
        BossDef d = new BossDef(id, 1);
        DEFS.put(id, d);
        return d;
    }

    private static MobEffectInstance fx(MobEffect e, int ticks, int level) {
        return new MobEffectInstance(e, ticks, level, false, true, true);
    }

    private static MobEffectInstance bleed(int ticks, int level) {
        return new MobEffectInstance(BLEEDING, ticks, level, false, true, true);
    }

    // ------------------------------------------------------------------ Chapter 1: Skadi's trials
    static {
        def("cave_bear").on("naturalist:bear", "minecraft:polar_bear")
                .stats(300, 10, 6).scale(1.7f).reach(1.3f).bar(BossBarColor.RED)
                .ability(() -> new Roar(240, 10, 20, 0.8, SoundEvents.POLAR_BEAR_WARNING, 0.5f,
                        () -> fx(MobEffects.MOVEMENT_SLOWDOWN, 80, 1), () -> fx(MobEffects.WEAKNESS, 100, 0)))
                .ability(() -> new Maul(160, 3, 7, 0.7))
                .ability(() -> new Slam(300, 14, 5, 1.0, 0.5, null))
                .drop("vividlands_ragnarok:bear_pelt", 1).xp(300)
                .biomes("vividlands:taiga_lakelands", "vividlands:caledonian_pinewood", "vividlands:boreal_snowwoods",
                        "#minecraft:is_taiga");

        def("irish_elk").on("fossil:megaloceros", "minecraft:goat")
                .stats(360, 11, 6).scale(1.3f).melee(Melee.BOSS).reach(1.6f).knockback(1.4f).bar(BossBarColor.GREEN)
                .ability(() -> new Charge(160, 18, 40, 0.75, 1.3, 2.2, false, 50))
                .ability(() -> new Summon(500, 2, 3, 40, 0.4f))
                .ability(() -> new Slam(260, 12, 4, 0.9, 0.6, null))
                .drop("vividlands_ragnarok:great_antlers", 1).xp(320).after(0)
                .biomes("vividlands:highland_moors", "vividlands:alpine_meadow", "minecraft:meadow");

        def("hippo").on("naturalist:hippo", "minecraft:ravager")
                .stats(420, 14, 8).scale(1.5f).reach(1.4f).bar(BossBarColor.PURPLE)
                .ability(() -> new Leap(200, 15, 3, 14, 1.3, 0.5, true, null))
                .ability(() -> new Capsize(160, 20, 60))
                .ability(() -> new Maul(220, 2, 12, 1.0))
                .drop("vividlands_ragnarok:hippo_hide", 1).xp(340)
                .biomes("vividlands:oasis", "vividlands:tropical_river", "minecraft:river");

        def("crocodile").on("naturalist:alligator")
                .stats(480, 13, 10).scale(2.0f).reach(1.2f).bar(BossBarColor.GREEN)
                .ability(() -> new DeathRoll(260, 60, 1.0, 0.08f))
                .ability(() -> new Leap(180, 10, 3, 12, 1.1, 0.35, true, null))
                .ability(() -> new Slam(240, 10, 4, 0.8, 0.4, null))
                .drop("vividlands_ragnarok:croc_scales", 1).xp(360).after("hippo")
                .biomes("vividlands:fen", "vividlands:tropical_river", "minecraft:swamp", "minecraft:mangrove_swamp");

        def("silverback").on("animalgarden_westerngorilla:westerngorilla", "minecraft:iron_golem")
                .stats(550, 14, 8).scale(2.0f).reach(1.4f).bar(BossBarColor.WHITE)
                .ability(() -> new Roar(260, 9, 20, 1.2, SoundEvents.RAVAGER_ROAR, 1.3f,
                        () -> BossFight.stunEffect(40), () -> fx(MobEffects.WEAKNESS, 100, 0)))
                .ability(() -> new Throw(180, 16, 2, 10, 0.9))
                .ability(() -> new Slam(220, 14, 6, 1.1, 0.8, null))
                .drop("vividlands_ragnarok:silverback_fist", 1).xp(400).after(3)
                .structures("ancientstructures:mayan_temple", "ancientstructures:mayan_temple2",
                        "ancientstructures:mayan_temple3", "ancientstructures:mayan_temple4");

        def("saber_tooth").on("fossil:smilodon", "minecraft:wolf")
                .stats(520, 15, 6).scale(1.3f).melee(Melee.BOSS).reach(1.1f).interval(18).bar(BossBarColor.YELLOW)
                .onHit(() -> bleed(100, 0))
                .ability(() -> new Stalk(9))
                .ability(() -> new Leap(140, 10, 5, 16, 1.4, 0.45, false, () -> bleed(160, 1)))
                .ability(() -> new Maul(200, 4, 6, 0.6))
                .drop("vividlands_ragnarok:saber_fang", 1).xp(420).after(4)
                .biomes("vividlands:endless_steppe", "vividlands:golden_savanna", "vividlands:wildflower_prairie",
                        "minecraft:savanna");

        def("woolly_rhino").on("fossil:elasmotherium", "naturalist:rhino", "minecraft:ravager")
                .stats(700, 16, 12).scale(1.2f).melee(Melee.BOSS).reach(1.5f).knockback(1.2f).bar(BossBarColor.WHITE)
                .ability(() -> new Charge(140, 20, 50, 0.85, 1.5, 2.6, true, 80))
                .ability(() -> new Slam(260, 14, 5, 0.9, 0.5, () -> fx(MobEffects.MOVEMENT_SLOWDOWN, 60, 1)))
                .drop("vividlands_ragnarok:rhino_horn", 1).xp(450).after("cave_bear")
                .biomes("vividlands:tundra", "vividlands:glacial_outwash", "minecraft:snowy_plains");

        def("elephant").on("naturalist:elephant", "minecraft:ravager")
                .stats(850, 17, 10).scale(1.3f).reach(1.8f).knockback(1.2f).bar(BossBarColor.YELLOW)
                .ability(() -> new Charge(200, 24, 60, 0.7, 1.4, 2.4, false, 60))
                .ability(() -> new Fling(160, 12, 0.8, 1.5, 0.4))
                .ability(() -> new Roar(300, 14, 20, 1.6, SoundEvents.RAVAGER_ROAR, 1.6f,
                        () -> fx(MobEffects.WEAKNESS, 120, 0), () -> fx(MobEffects.MOVEMENT_SLOWDOWN, 60, 0)))
                .ability(() -> new Slam(260, 16, 6, 1.0, 0.6, null))
                .drop("vividlands_ragnarok:ivory", 2).xp(500).after(6)
                .biomes("vividlands:golden_savanna", "minecraft:savanna", "minecraft:savanna_plateau");

        def("bull_shark").on("animalgarden_bullshark:bullshark", "minecraft:dolphin")
                .stats(650, 16, 6).scale(2.5f).melee(Melee.BOSS).reach(1.0f).interval(20).inSea().bar(BossBarColor.BLUE)
                .onHit(() -> bleed(100, 0))
                .ability(() -> new Leap(160, 14, 3, 14, 1.3, 0.7, true, () -> bleed(160, 1)))
                .ability(() -> new Capsize(140, 20, 80))
                .ability(() -> new Maul(200, 3, 8, 0.6))
                .drop("vividlands_ragnarok:shark_tooth", 2).xp(480).after("crocodile")
                .biomes("vividlands:northern_ocean", "vividlands:temperate_ocean", "vividlands:deep_northern_ocean",
                        "vividlands:deep_temperate_ocean", "#minecraft:is_deep_ocean");

        def("mammoth").on("fossil:mammoth", "minecraft:ravager")
                .stats(1000, 20, 14).scale(1.4f).melee(Melee.BOSS).reach(2.0f).knockback(1.4f).interval(30).bar(BossBarColor.WHITE)
                .ability(() -> new Shockwave(260, 24, 16, 0.5, 1.0))
                .ability(() -> new Slam(220, 18, 7, 1.2, 0.8, () -> fx(MobEffects.MOVEMENT_SLOWDOWN, 80, 2)))
                .ability(() -> new Charge(240, 26, 50, 0.7, 1.6, 3.0, true, 60))
                .ability(() -> new Fling(200, 14, 0.9, 1.6, 0.6))
                .drop("vividlands_ragnarok:mammoth_tusk", 2).drop("vividlands_ragnarok:frozen_heart", 1).xp(1000).after(9)
                .biomes("vividlands:glacier", "vividlands:glacier_peaks", "minecraft:ice_spikes");
    }

    // ------------------------------------------------------------------ lookups
    public static String bossId(Entity e) {
        return e instanceof BossHolder h ? h.vlr$boss() : null;
    }

    public static boolean isBoss(Entity e) {
        return bossId(e) != null;
    }

    public static boolean isMinion(Entity e) {
        return e != null && e.getTags().contains(MINION_TAG);
    }

    public static BossDef defOf(Entity e) {
        String id = bossId(e);
        return id == null ? null : DEFS.get(id);
    }

    /** Size multiplier for hitbox (both sides) and rendering (client). */
    public static float scaleOf(Entity e) {
        BossDef d = defOf(e);
        return d == null ? 1f : d.scale;
    }

    public static Collection<BossFight> fights() {
        return FIGHTS.values();
    }

    static Optional<EntityType<?>> typeOf(BossDef def) {
        for (String id : def.entities) {
            Optional<EntityType<?>> t = BuiltInRegistries.ENTITY_TYPE.getOptional(new ResourceLocation(id));
            if (t.isPresent()) return t;
        }
        return Optional.empty();
    }

    // ------------------------------------------------------------------ spawning
    /** Spawns the boss at pos. @return the boss, or null if none of its creatures exist in this pack */
    public static Mob spawn(ServerLevel level, BossDef def, Vec3 pos) {
        Optional<EntityType<?>> type = typeOf(def);
        if (type.isEmpty()) return null;
        Entity e = type.get().create(level);
        if (!(e instanceof Mob mob)) {
            if (e != null) e.discard();
            return null;
        }
        mob.moveTo(pos.x, pos.y, pos.z, level.random.nextFloat() * 360f, 0f);
        mob.finalizeSpawn(level, level.getCurrentDifficultyAt(mob.blockPosition()), MobSpawnType.COMMAND, null, null);
        Compat.grownUp(mob);
        mob.addTag(TAG + def.id);
        mob.setCustomName(Component.translatable(def.nameKey()).withStyle(ChatFormatting.GOLD));
        mob.setPersistenceRequired();
        AttributeInstance speed = mob.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) speed.setBaseValue(speed.getBaseValue() * def.speed);
        applyStats(mob, def);
        mob.setHealth(mob.getMaxHealth());
        level.addFreshEntityWithPassengers(mob);
        return mob;
    }

    private static void setBase(Mob mob, net.minecraft.world.entity.ai.attributes.Attribute a, double v) {
        AttributeInstance i = mob.getAttribute(a);
        if (i != null) i.setBaseValue(v);
    }

    private static final UUID HEALTH_ID = UUID.fromString("0b7d3c1e-5a2f-4c8e-9b6d-2e4f6a8c0d11");
    private static final UUID ARMOR_ID = UUID.fromString("0b7d3c1e-5a2f-4c8e-9b6d-2e4f6a8c0d12");
    private static final UUID DAMAGE_ID = UUID.fromString("0b7d3c1e-5a2f-4c8e-9b6d-2e4f6a8c0d13");

    /**
     * Sets an attribute to the boss's value with a saved modifier on top of whatever base the creature mod uses
     * (some mods, like Fossils and Archeology, keep resetting the base value as their animals grow).
     */
    private static boolean target(Mob mob, net.minecraft.world.entity.ai.attributes.Attribute a, UUID id, double want) {
        AttributeInstance inst = mob.getAttribute(a);
        if (inst == null) return false;
        double amount = want - inst.getBaseValue();
        var m = inst.getModifier(id);
        if (m != null && Math.abs(m.getAmount() - amount) < 1e-3) return false;
        if (m != null) inst.removeModifier(id);
        inst.addPermanentModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(id, "vividlands boss",
                amount, net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION));
        return true;
    }

    /** Applied on load and every second, so balancing changes reach existing bosses and nothing can undo them. */
    static void applyStats(Mob mob, BossDef def) {
        float frac = mob.getMaxHealth() > 0 ? mob.getHealth() / mob.getMaxHealth() : 1f;
        boolean changed = target(mob, Attributes.MAX_HEALTH, HEALTH_ID, def.health);
        target(mob, Attributes.ARMOR, ARMOR_ID, def.armor);
        target(mob, Attributes.ATTACK_DAMAGE, DAMAGE_ID, def.damage);
        setBase(mob, Attributes.KNOCKBACK_RESISTANCE, 0.75);
        setBase(mob, Attributes.FOLLOW_RANGE, 48);
        if (changed && mob.getHealth() > 0) mob.setHealth(Math.max(1f, frac * mob.getMaxHealth()));
    }

    /** Turns a loaded mob carrying a boss tag into a running boss. */
    private static void attach(Mob mob, BossDef def) {
        ((BossHolder) mob).vlr$setBoss(def.id);
        mob.refreshDimensions();
        applyStats(mob, def);
        mob.setPersistenceRequired();
        BossFight fight = new BossFight(mob, def);
        // BOSS melee: the pack's goal comes first. OWN melee: the creature's attack goal comes first, and the pack's
        // goal only takes over when that one gives up (so the boss never wanders off mid-fight).
        boolean own = def.melee == Melee.OWN && mob.getAttribute(Attributes.ATTACK_DAMAGE) != null;
        ((MobGoalsAccessor) mob).vlr$goals().addGoal(own ? 3 : 0, new BossMeleeGoal(mob, () -> FIGHTS.get(mob), def.damage,
                def.reach, def.attackInterval));
        FIGHTS.put(mob, fight);
        debug("{} is {} ({}), {} hp, {}x{} hitbox", def.id, BuiltInRegistries.ENTITY_TYPE.getKey(mob.getType()),
                mob.getClass().getSimpleName(), mob.getMaxHealth(), mob.getBbWidth(), mob.getBbHeight());
        for (ServerPlayer p : PlayerLookup.tracking(mob)) sync(p, mob);
    }

    public static int minionCount(BossFight f) {
        f.minions.removeIf(m -> !m.isAlive());
        return f.minions.size();
    }

    public static void spawnMinion(BossFight f, float health, float damage) {
        Mob boss = f.mob();
        Entity e = boss.getType().create(f.level());
        if (!(e instanceof Mob m)) return;
        double a = boss.getRandom().nextDouble() * Math.PI * 2;
        double r = boss.getBbWidth() + 2 + boss.getRandom().nextDouble() * 3;
        double x = boss.getX() + Math.cos(a) * r, z = boss.getZ() + Math.sin(a) * r;
        int y = f.level().getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, (int) Math.floor(x), (int) Math.floor(z));
        m.moveTo(x, Math.abs(y - boss.getY()) < 6 ? y : boss.getY(), z, boss.getYRot(), 0f);
        m.finalizeSpawn(f.level(), f.level().getCurrentDifficultyAt(m.blockPosition()), MobSpawnType.MOB_SUMMONED, null, null);
        Compat.grownUp(m);
        m.addTag(MINION_TAG);
        setBase(m, Attributes.MAX_HEALTH, health);
        setBase(m, Attributes.ATTACK_DAMAGE, damage);
        m.setHealth(health);
        ((MobGoalsAccessor) m).vlr$goals().addGoal(0, new BossMeleeGoal(m, null, damage, 1.0f, 26));
        m.setTarget(f.target());
        addingMinion = true;
        try {
            f.level().addFreshEntity(m);
        } finally {
            addingMinion = false;
        }
        f.particles(net.minecraft.core.particles.ParticleTypes.POOF, m.getX(), m.getY() + 0.5, m.getZ(), 12, 0.5, 0.5, 0.5, 0.05);
        f.minions.add(m);
    }

    // ------------------------------------------------------------------ progress
    public static int chapterOneBeaten(Set<String> defeated) {
        int n = 0;
        for (String id : defeated) {
            BossDef d = DEFS.get(id);
            if (d != null && d.chapter == 1) n++;
        }
        return n;
    }

    public static boolean unlocked(BossDef def, Set<String> defeated) {
        if (!defeated.containsAll(def.requires)) return false;
        int n = chapterOneBeaten(defeated) - (defeated.contains(def.id) ? 1 : 0);
        return n >= def.requiresCount;
    }

    private static void reward(Mob mob, BossDef def) {
        ServerLevel level = (ServerLevel) mob.level();
        for (String[] d : def.drops) {
            Item item = BuiltInRegistries.ITEM.get(new ResourceLocation(d[0]));
            mob.spawnAtLocation(new ItemStack(item, Integer.parseInt(d[1])), 1f);
        }
        ExperienceOrb.award(level, mob.position(), def.xp);
        BossFight fight = FIGHTS.get(mob);
        Set<UUID> winners = new HashSet<>(fight != null ? fight.fighters() : Set.of());
        for (ServerPlayer p : level.players()) {
            if (p.distanceTo(mob) < 64) winners.add(p.getUUID());
        }
        BossProgress progress = BossProgress.get(level.getServer());
        Component name = Component.translatable(def.nameKey()).withStyle(ChatFormatting.GOLD);
        for (UUID u : winners) {
            progress.defeat(u, def.id);
            ServerPlayer p = level.getServer().getPlayerList().getPlayer(u);
            if (p == null) continue;
            p.sendSystemMessage(Component.translatable("boss.vividlands_ragnarok.slain", name));
            if (def.chapter == 1) {
                p.sendSystemMessage(Component.translatable("boss.vividlands_ragnarok.trials",
                        chapterOneBeaten(progress.defeated(u)), chapterOneCount()).withStyle(ChatFormatting.AQUA));
            }
            level.playSound(null, p.getX(), p.getY(), p.getZ(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1f, 1f);
        }
    }

    public static int chapterOneCount() {
        return (int) DEFS.values().stream().filter(d -> d.chapter == 1).count();
    }

    // ------------------------------------------------------------------ client sync
    private static void sync(ServerPlayer p, Entity e) {
        String id = bossId(e);
        if (id == null) return;
        FriendlyByteBuf buf = PacketByteBufs.create();
        buf.writeVarInt(e.getId());
        buf.writeUtf(id);
        ServerPlayNetworking.send(p, PACKET, buf);
    }

    // ------------------------------------------------------------------ setup
    public static void register() {
        BLEEDING = Registry.register(BuiltInRegistries.MOB_EFFECT, new ResourceLocation(Ragnarok.MOD_ID, "bleeding"), new Bleeding());
        BOULDER = Registry.register(BuiltInRegistries.ENTITY_TYPE, new ResourceLocation(Ragnarok.MOD_ID, "boulder"),
                EntityType.Builder.<Boulder>of(Boulder::new, MobCategory.MISC).sized(0.9f, 0.9f)
                        .clientTrackingRange(8).updateInterval(10).build("boulder"));
        SPAWNING = GameRuleRegistry.register("vividlandsBossSpawning", GameRules.Category.SPAWNING,
                GameRuleFactory.createBooleanRule(true));

        ServerEntityEvents.ENTITY_LOAD.register((entity, level) -> {
            if (!(entity instanceof Mob mob)) return;
            if (isMinion(mob)) {               // minions only live as long as the fight they were called into
                if (addingMinion) return;
                mob.discard();
                return;
            }
            for (String tag : mob.getTags()) {
                if (tag.startsWith(TAG)) {
                    BossDef def = DEFS.get(tag.substring(TAG.length()));
                    if (def != null && !FIGHTS.containsKey(mob)) attach(mob, def);
                    return;
                }
            }
        });
        ServerEntityEvents.ENTITY_UNLOAD.register((entity, level) -> {
            if (entity instanceof Mob mob) {
                BossFight f = FIGHTS.remove(mob);
                if (f != null) f.close();
            }
        });
        ServerTickEvents.END_WORLD_TICK.register(level -> {
            List<BossFight> list = new ArrayList<>();
            for (BossFight f : FIGHTS.values()) if (f.level() == level) list.add(f);
            for (BossFight f : list) {
                f.tick();
                for (Mob m : f.minions) {
                    if (m.isAlive() && f.target() != null && m.getTarget() != f.target()) m.setTarget(f.target());
                }
            }
            BossSpawner.tick(level);
        });
        EntityTrackingEvents.START_TRACKING.register((entity, player) -> {
            if (isBoss(entity)) sync(player, entity);
        });
        ServerLivingEntityEvents.ALLOW_DAMAGE.register((entity, source, amount) -> {
            Entity attacker = source.getEntity();
            boolean environment = source.is(DamageTypeTags.IS_FALL) || source.is(DamageTypes.IN_WALL)
                    || source.is(DamageTypes.CRAMMING) || source.is(DamageTypes.DROWN) || source.is(DamageTypes.FLY_INTO_WALL);
            if (isBoss(entity)) {
                if (environment || isBoss(attacker) || isMinion(attacker)) return false;
                BossFight f = FIGHTS.get(entity);
                if (f != null) f.onDamaged(amount, attacker);
            } else if (isMinion(entity) && (environment || isBoss(attacker) || isMinion(attacker))) {
                return false;
            }
            BossDef def = defOf(attacker);
            if (def != null) debug("{} deals {} to {} ({})", def.id, amount, entity.getType().getDescriptionId(), source.getMsgId());
            if (def != null && source.getDirectEntity() == attacker && !isBoss(entity)) {
                for (var e : def.onHit) entity.addEffect(e.get(), attacker);
            }
            return true;
        });
        ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
            if (!(entity instanceof Mob mob)) return;
            BossDef def = defOf(mob);
            if (def == null) return;
            debug("{} died ({})", def.id, source.getMsgId());
            reward(mob, def);
            BossFight f = FIGHTS.remove(mob);
            if (f != null) f.close();
        });
        UseEntityCallback.EVENT.register((player, world, hand, entity, hit) ->
                isBoss(entity) || isMinion(entity) ? InteractionResult.FAIL : InteractionResult.PASS);
        BossCommands.register();
        Ragnarok.LOG.info("Vivid Lands: Ragnarok - {} bosses", DEFS.size());
    }

    static boolean fightable(Player p) {
        return !p.isCreative() && !p.isSpectator();
    }
}
