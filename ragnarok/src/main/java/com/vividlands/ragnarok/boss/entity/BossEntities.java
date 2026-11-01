package com.vividlands.ragnarok.boss.entity;

import com.vividlands.ragnarok.Ragnarok;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Entity types for the pack's own boss models (vividlands_ragnarok:<boss id>). The size given here is the model
 * at 1x; BossDef.scale makes it huge.
 */
public final class BossEntities {
    public static final Map<String, EntityType<?>> TYPES = new LinkedHashMap<>();

    private BossEntities() {
    }

    private static AttributeSupplier.Builder attributes() {
        return Mob.createMobAttributes().add(Attributes.ATTACK_DAMAGE, 8).add(Attributes.MOVEMENT_SPEED, 0.3)
                .add(Attributes.FOLLOW_RANGE, 48).add(Attributes.KNOCKBACK_RESISTANCE, 0.75).add(Attributes.ARMOR, 4);
    }

    private static void land(String id, float w, float h, double speed) {
        EntityType<LandBoss> t = Registry.register(BuiltInRegistries.ENTITY_TYPE, new ResourceLocation(Ragnarok.MOD_ID, id),
                EntityType.Builder.<LandBoss>of(LandBoss::new, MobCategory.MONSTER).sized(w, h).clientTrackingRange(10).build(id));
        FabricDefaultAttributeRegistry.register(t, attributes().add(Attributes.MOVEMENT_SPEED, speed));
        TYPES.put(id, t);
    }

    private static void sea(String id, float w, float h, double speed) {
        EntityType<SeaBoss> t = Registry.register(BuiltInRegistries.ENTITY_TYPE, new ResourceLocation(Ragnarok.MOD_ID, id),
                EntityType.Builder.<SeaBoss>of(SeaBoss::new, MobCategory.WATER_CREATURE).sized(w, h).clientTrackingRange(10).build(id));
        FabricDefaultAttributeRegistry.register(t, attributes().add(Attributes.MOVEMENT_SPEED, speed));
        TYPES.put(id, t);
    }

    private static void fly(String id, float w, float h, double speed) {
        EntityType<FlyingBoss> t = Registry.register(BuiltInRegistries.ENTITY_TYPE, new ResourceLocation(Ragnarok.MOD_ID, id),
                EntityType.Builder.<FlyingBoss>of(FlyingBoss::new, MobCategory.MONSTER).sized(w, h).clientTrackingRange(12).build(id));
        FabricDefaultAttributeRegistry.register(t, attributes().add(Attributes.MOVEMENT_SPEED, speed).add(Attributes.FLYING_SPEED, speed * 1.6));
        TYPES.put(id, t);
    }

    public static void register() {
        land("cave_bear", 1.0f, 1.5f, 0.3);
        land("irish_elk", 1.0f, 2.0f, 0.32);
        land("hippo", 1.2f, 1.4f, 0.27);
        land("crocodile", 1.2f, 0.6f, 0.28);
        land("silverback", 1.1f, 1.9f, 0.3);
        land("saber_tooth", 0.8f, 1.2f, 0.36);
        land("woolly_rhino", 1.1f, 1.8f, 0.3);
        land("elephant", 1.6f, 2.6f, 0.27);
        sea("bull_shark", 1.0f, 0.7f, 1.2);
        land("mammoth", 1.6f, 3.2f, 0.27);
        // trials 11-20
        land("dire_wolf", 0.8f, 1.2f, 0.36);
        land("steppe_bison", 1.1f, 1.7f, 0.3);
        land("terror_bird", 0.8f, 2.3f, 0.38);
        land("komodo", 0.9f, 0.6f, 0.28);
        land("glyptodon", 1.2f, 1.3f, 0.24);
        land("cave_lion", 0.9f, 1.3f, 0.35);
        land("anaconda", 0.8f, 0.6f, 0.3);
        land("ground_sloth", 1.1f, 2.0f, 0.26);
        fly("haast_eagle", 1.0f, 0.9f, 0.3);
        land("walrus", 1.2f, 1.1f, 0.24);
        // Chapter 2: Odin's war against Ragnarok
        land("sleipnir", 1.0f, 2.2f, 0.36);
        land("garmr", 0.9f, 1.4f, 0.34);
        land("fafnir", 1.2f, 1.6f, 0.3);
        sea("jormungandr", 1.0f, 0.9f, 1.3);
        land("fenrir", 1.0f, 1.45f, 0.34);
    }
}
