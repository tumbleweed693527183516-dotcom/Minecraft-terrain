package com.vividlands.ragnarok.boss;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Natural boss appearances (Overworld, gamerule vividlandsBossSpawning).
 *  - Wild bosses: every 30 s each player in a boss's home biome has a 1 in 6 chance to meet it, 28-48 blocks away,
 *    if no other boss is near, the boss is unlocked for that player, and it hasn't appeared in this
 *    1024 x 1024 region before.
 *  - Structure bosses (the Silverback): appear once per structure, when a player who has unlocked them walks in.
 */
final class BossSpawner {
    private static final int REGION_SHIFT = 10;
    private static final Set<String> TOLD = new HashSet<>();     // "locked" hints already shown this session

    private BossSpawner() {
    }

    static void tick(ServerLevel level) {
        if (level.dimension() != Level.OVERWORLD || !level.getGameRules().getBoolean(Bosses.SPAWNING)) return;
        long t = level.getGameTime();
        if (t % 100 == 40) structures(level);
        if (t % 600 == 300) wild(level);
    }

    private static boolean bossNear(ServerLevel level, Vec3 pos, double range) {
        for (BossFight f : Bosses.fights()) {
            if (f.level() == level && f.mob().position().distanceTo(pos) < range) return true;
        }
        return false;
    }

    static boolean biomeMatches(BossDef def, Holder<Biome> biome) {
        for (String b : def.biomes) {
            if (b.startsWith("#")) {
                if (biome.is(TagKey.create(Registries.BIOME, new ResourceLocation(b.substring(1))))) return true;
            } else if (biome.is(new ResourceLocation(b))) {
                return true;
            }
        }
        return false;
    }

    private static void wild(ServerLevel level) {
        BossProgress progress = BossProgress.get(level.getServer());
        RandomSource rnd = level.random;
        for (ServerPlayer p : level.players()) {
            if (!Bosses.fightable(p) || bossNear(level, p.position(), 160)) continue;
            if (rnd.nextInt(6) != 0) continue;
            Holder<Biome> here = level.getBiome(p.blockPosition());
            Set<String> beaten = progress.defeated(p.getUUID());
            List<BossDef> options = new ArrayList<>();
            for (BossDef d : Bosses.DEFS.values()) {
                if (d.biomes.isEmpty() || !biomeMatches(d, here) || !Bosses.unlocked(d, beaten)) continue;
                if (progress.spawnedAt(regionKey(d, p.blockPosition()))) continue;
                options.add(d);
            }
            if (options.isEmpty()) continue;
            BossDef d = options.get(rnd.nextInt(options.size()));
            Vec3 at = findSpot(level, d, p.position(), 28, 48, null);
            if (at == null) continue;
            if (Bosses.spawn(level, d, at) != null) progress.markSpawned(regionKey(d, p.blockPosition()));
        }
    }

    private static String regionKey(BossDef d, BlockPos pos) {
        return d.id + "@" + (pos.getX() >> REGION_SHIFT) + "," + (pos.getZ() >> REGION_SHIFT);
    }

    private static void structures(ServerLevel level) {
        var registry = level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        BossProgress progress = BossProgress.get(level.getServer());
        for (ServerPlayer p : level.players()) {
            if (!Bosses.fightable(p)) continue;
            for (BossDef d : Bosses.DEFS.values()) {
                for (String sid : d.structures) {
                    Structure s = registry.get(new ResourceLocation(sid));
                    if (s == null) continue;
                    StructureStart start = level.structureManager().getStructureWithPieceAt(p.blockPosition(), s);
                    if (!start.isValid()) continue;
                    String key = d.id + "@" + sid + "@" + start.getChunkPos().x + "," + start.getChunkPos().z;
                    if (progress.spawnedAt(key)) continue;
                    if (!Bosses.unlocked(d, progress.defeated(p.getUUID()))) {
                        if (TOLD.add(p.getUUID() + key)) {
                            p.displayClientMessage(Component.translatable("boss.vividlands_ragnarok.locked",
                                    Component.translatable(d.nameKey())), true);
                        }
                        continue;
                    }
                    if (bossNear(level, p.position(), 96)) continue;
                    Vec3 at = findSpot(level, d, p.position(), 14, 30, start.getBoundingBox());
                    if (at != null && Bosses.spawn(level, d, at) != null) progress.markSpawned(key);
                }
            }
        }
    }

    /** A free spot for the boss min-max blocks from the player (in water for sea bosses, inside box if given). */
    static Vec3 findSpot(ServerLevel level, BossDef d, Vec3 around, double min, double max, BoundingBox box) {
        Optional<EntityType<?>> type = Bosses.typeOf(d);
        if (type.isEmpty()) return null;
        RandomSource rnd = level.random;
        for (int i = 0; i < 24; i++) {
            double a = rnd.nextDouble() * Math.PI * 2, r = min + rnd.nextDouble() * (max - min);
            int x = (int) Math.floor(around.x + Math.cos(a) * r), z = (int) Math.floor(around.z + Math.sin(a) * r);
            if (!level.hasChunkAt(new BlockPos(x, 0, z))) continue;
            double y;
            if (d.aquatic) {
                int surface = level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
                int floor = level.getHeight(Heightmap.Types.OCEAN_FLOOR, x, z);
                if (surface - floor < 5 || !level.getFluidState(new BlockPos(x, surface - 1, z)).is(FluidTags.WATER)) continue;
                y = floor + (surface - floor) * 0.5;
            } else if (box != null) {
                // structure bosses are far too big for the rooms: they wait on the ground around (or on top of) it
                if (x < box.minX() - 6 || x > box.maxX() + 6 || z < box.minZ() - 6 || z > box.maxZ() + 6) continue;
                y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            } else {
                y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
                if (!level.getFluidState(new BlockPos(x, (int) y - 1, z)).isEmpty() && d.melee != BossDef.Melee.OWN) continue;
            }
            BlockPos at = BlockPos.containing(x + 0.5, y, z + 0.5);
            if (!d.biomes.isEmpty() && box == null && !biomeMatches(d, level.getBiome(at))) continue;
            // only the space around its legs has to be free: it tramples leaves and plants once it moves
            AABB aabb = new AABB(x + 0.5 - 1, y + 0.05, z + 0.5 - 1, x + 0.5 + 1, y + 3, z + 0.5 + 1);
            if (!level.noCollision(aabb)) continue;
            return new Vec3(x + 0.5, y, z + 0.5);
        }
        return null;
    }

    /** Standable floor near y (inside a structure: temples have floors at many heights). */
    private static double groundIn(ServerLevel level, int x, int y, int z) {
        for (int dy = 6; dy >= -8; dy--) {
            BlockPos p = new BlockPos(x, y + dy, z);
            if (level.getBlockState(p.below()).isFaceSturdy(level, p.below(), net.minecraft.core.Direction.UP)
                    && level.getBlockState(p).getCollisionShape(level, p).isEmpty()
                    && level.getBlockState(p.above()).getCollisionShape(level, p.above()).isEmpty()) {
                return y + dy;
            }
        }
        return Double.NaN;
    }
}
