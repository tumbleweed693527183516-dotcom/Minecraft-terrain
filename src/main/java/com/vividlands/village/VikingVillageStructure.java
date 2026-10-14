package com.vividlands.village;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiecesBuilder;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.level.material.Fluids;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * A walled Viking village: a sharpened-log palisade ring that follows the ground, gatehouses,
 * watchtowers, a central plaza, a chieftain's hall, craft and civic buildings, houses laid out
 * without overlap with doors facing the centre, dirt paths, and fields outside the walls.
 */
public class VikingVillageStructure extends Structure {
    public static final Codec<VikingVillageStructure> CODEC = simpleCodec(VikingVillageStructure::new);

    private static final int MAX_SLOPE = 34;

    public VikingVillageStructure(StructureSettings settings) {
        super(settings);
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.VIKING_VILLAGE;
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        RandomSource rand = ctx.random();
        int cx = ctx.chunkPos().getMiddleBlockX();
        int cz = ctx.chunkPos().getMiddleBlockZ();
        int centreY = height(ctx, cx, cz);
        if (isWater(ctx, cx, centreY, cz)) {
            return Optional.empty();
        }
        double big = 50 + rand.nextInt(13);
        Ring ringShape = new Ring(cx, cz, big, rand);
        // try a large village first, then shrink to fit rougher ground
        for (double radius : new double[]{big, big - 10, big - 18}) {
            Ring ring = new Ring(cx, cz, radius, ringShape.a1, ringShape.p1, ringShape.a2, ringShape.p2);
            List<Integer> heights = new ArrayList<>();
            int wet = 0;
            for (int i = 0; i < 16; i++) {
                double a = i * Math.PI / 8;
                for (double f : new double[]{0.95, 0.5}) {
                    int x = (int) Math.round(cx + Math.cos(a) * ring.radiusAt(a) * f);
                    int z = (int) Math.round(cz + Math.sin(a) * ring.radiusAt(a) * f);
                    int y = height(ctx, x, z);
                    heights.add(y);
                    if (f == 0.5 && isWater(ctx, x, y, z)) {
                        wet++;
                    }
                }
            }
            Collections.sort(heights);
            if (wet > 5 || heights.get(heights.size() - 3) - heights.get(2) > MAX_SLOPE) {
                continue;
            }
            int groundY = heights.get(heights.size() / 2);
            return Optional.of(new GenerationStub(new BlockPos(cx, groundY, cz),
                    builder -> new Planner(ctx, ring, groundY).build(builder)));
        }
        return Optional.empty();
    }

    static int height(GenerationContext ctx, int x, int z) {
        return ctx.chunkGenerator().getFirstOccupiedHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG,
                ctx.heightAccessor(), ctx.randomState());
    }

    static boolean isWater(GenerationContext ctx, int x, int y, int z) {
        return ctx.chunkGenerator().getBaseColumn(x, z, ctx.heightAccessor(), ctx.randomState()).getBlock(y)
                .getFluidState().is(Fluids.WATER);
    }

    /** Slightly wobbly circle, so walls look hand-built rather than compass-drawn. */
    static final class Ring {
        final int cx, cz;
        final double radius, a1, p1, a2, p2;

        Ring(int cx, int cz, double radius, RandomSource rand) {
            this(cx, cz, radius, 0.05 + rand.nextDouble() * 0.03, rand.nextDouble() * Math.PI * 2,
                    0.03 + rand.nextDouble() * 0.02, rand.nextDouble() * Math.PI * 2);
        }

        Ring(int cx, int cz, double radius, double a1, double p1, double a2, double p2) {
            this.cx = cx;
            this.cz = cz;
            this.radius = radius;
            this.a1 = a1;
            this.p1 = p1;
            this.a2 = a2;
            this.p2 = p2;
        }

        double radiusAt(double angle) {
            return radius * (1 + a1 * Math.sin(2 * angle + p1) + a2 * Math.sin(3 * angle + p2));
        }

        double angleOf(double x, double z) {
            double a = Math.atan2(z - cz, x - cx);
            return a < 0 ? a + Math.PI * 2 : a;
        }

        boolean inside(double x, double z, double margin) {
            double d = Math.hypot(x - cx, z - cz);
            return d < radiusAt(angleOf(x, z)) - margin;
        }
    }

    /** Lays out one village. */
    static final class Planner {
        private final GenerationContext ctx;
        private final RandomSource rand;
        private final Ring ring;
        private final int groundY;
        private final List<int[]> rects = new ArrayList<>();      // minX, minZ, maxX, maxZ
        private final List<int[]> doors = new ArrayList<>();      // x, z, target x, target z, outside?
        private final List<int[]> gates = new ArrayList<>();
        private final Set<Long> paths = new HashSet<>();

        Planner(GenerationContext ctx, Ring ring, int groundY) {
            this.ctx = ctx;
            this.rand = ctx.random();
            this.ring = ring;
            this.groundY = groundY;
        }

        void build(StructurePiecesBuilder out) {
            VillageCatalogue cat = VillageCatalogue.get();
            int cx = ring.cx, cz = ring.cz;

            // plaza in the middle
            place(out, cat.pick("plaza", rand), cx, cz, Rotation.getRandom(rand), false);
            int plazaHalf = 11;

            // gates on 2-3 of the 4 sides
            List<Integer> sides = new ArrayList<>(List.of(0, 1, 2, 3));
            Collections.shuffle(sides, new java.util.Random(rand.nextLong()));
            int gateCount = 2 + rand.nextInt(2);
            for (int i = 0; i < gateCount; i++) {
                int side = sides.get(i);                         // 0 east, 1 south, 2 west, 3 north
                double a = side * Math.PI / 2;
                double r = ring.radiusAt(a);
                int gx = (int) Math.round(cx + Math.cos(a) * r);
                int gz = (int) Math.round(cz + Math.sin(a) * r);
                Rotation rot = switch (side) {
                    case 0 -> Rotation.CLOCKWISE_90;
                    case 1 -> Rotation.CLOCKWISE_180;
                    case 2 -> Rotation.COUNTERCLOCKWISE_90;
                    default -> Rotation.NONE;
                };
                place(out, cat.pick("wall_gate", rand), gx, gz, rot, true);
                gates.add(new int[]{gx, gz});
                // main road from the gate to the plaza
                int ix = (int) Math.round(cx + Math.cos(a) * (r - 5));
                int iz = (int) Math.round(cz + Math.sin(a) * (r - 5));
                road(ix, iz, cx, cz, 1, plazaHalf);
            }

            // watchtowers on the diagonals, just inside the wall
            for (int i = 0; i < 4; i++) {
                if (rand.nextFloat() < 0.6f) {
                    double a = Math.PI / 4 + i * Math.PI / 2 + (rand.nextDouble() - 0.5) * 0.3;
                    double r = ring.radiusAt(a) - 9;
                    place(out, cat.pick("wall_tower", rand), (int) Math.round(cx + Math.cos(a) * r),
                            (int) Math.round(cz + Math.sin(a) * r), Rotation.getRandom(rand), false);
                }
            }

            // buildings, most important first
            List<String> plan = new ArrayList<>();
            plan.add(cat.pick("core", rand));
            plan.addAll(cat.pickSome("civic", 1 + rand.nextInt(2), rand));
            plan.addAll(cat.pickSome("craft", 4 + rand.nextInt(3), rand));
            List<String> houses = cat.all("house");
            Collections.shuffle(houses, new java.util.Random(rand.nextLong()));
            plan.addAll(houses);
            plan.addAll(cat.pickSome("craft", 2, rand));
            int placed = 0;
            for (String id : plan) {
                if (tryPlaceInside(out, id, 90)) {
                    placed++;
                }
            }
            com.vividlands.VividLands.LOG.debug("Viking village at {}, {}: radius {}, {} buildings", cx, cz,
                    (int) ring.radius, placed);

            // fields and folds outside the walls, near the gates
            List<String> fields = cat.all("field");
            int fieldCount = 3 + rand.nextInt(3);
            for (int i = 0; i < fieldCount && !gates.isEmpty(); i++) {
                String id = fields.get(rand.nextInt(fields.size()));
                int[] g = gates.get(i % gates.size());
                tryPlaceOutside(out, id, g, 40);
            }

            // side paths: inside doors lead to the plaza, outside ones to their gate
            for (int[] d : doors) {
                road(d[0], d[1], d[2], d[3], 0, d[4] == 1 ? 2 : plazaHalf);
            }
            out.addPiece(new PathPiece(paths, groundY));

            // palisade in arc segments
            int segments = Math.max(8, (int) (ring.radius * 2 * Math.PI / 14));
            List<int[]> gateList = new ArrayList<>(gates);
            for (int i = 0; i < segments; i++) {
                double a0 = i * Math.PI * 2 / segments, a1 = (i + 1) * Math.PI * 2 / segments;
                out.addPiece(new PalisadePiece(ring, a0, a1, gateList, groundY));
            }
        }

        private boolean tryPlaceInside(StructurePiecesBuilder out, String id, int attempts) {
            Vec3i size = size(id);
            for (int i = 0; i < attempts; i++) {
                double a = rand.nextDouble() * Math.PI * 2;
                double maxR = ring.radiusAt(a) - Math.min(size.getX(), size.getZ()) / 2.0 - 4;
                if (maxR < 15) {
                    continue;
                }
                double r = 15 + rand.nextDouble() * (maxR - 15);
                int bx = (int) Math.round(ring.cx + Math.cos(a) * r);
                int bz = (int) Math.round(ring.cz + Math.sin(a) * r);
                Rotation facing = faceToward(bx, bz, ring.cx, ring.cz);
                Rotation[] options = size.getZ() >= 20
                        ? new Rotation[]{facing, facing.getRotated(Rotation.CLOCKWISE_90), facing.getRotated(Rotation.COUNTERCLOCKWISE_90)}
                        : new Rotation[]{facing};
                for (Rotation rot : options) {
                    int[] rect = rect(bx, bz, size, rot, 2);
                    if (!cornersInside(rect, 3) || overlaps(rect)) {
                        continue;
                    }
                    if (place(out, id, bx, bz, rot, false)) {
                        return true;
                    }
                }
            }
            return false;
        }

        private int[] nearestGate(int x, int z) {
            int[] best = new int[]{ring.cx, ring.cz};
            double bd = Double.MAX_VALUE;
            for (int[] g : gates) {
                double d = Math.hypot(g[0] - x, g[1] - z);
                if (d < bd) {
                    bd = d;
                    best = g;
                }
            }
            return best;
        }

        private void tryPlaceOutside(StructurePiecesBuilder out, String id, int[] gate, int attempts) {
            Vec3i size = size(id);
            double ga = ring.angleOf(gate[0], gate[1]);
            for (int i = 0; i < attempts; i++) {
                double a = ga + (rand.nextDouble() - 0.5) * 1.4;
                double r = ring.radiusAt(a) + 8 + rand.nextDouble() * 22;
                int bx = (int) Math.round(ring.cx + Math.cos(a) * r);
                int bz = (int) Math.round(ring.cz + Math.sin(a) * r);
                Rotation rot = Rotation.getRandom(rand);
                int[] rect = rect(bx, bz, size, rot, 2);
                if (anyCornerInside(rect, -3) || overlaps(rect)) {
                    continue;
                }
                if (place(out, id, bx, bz, rot, false)) {
                    return;
                }
            }
        }

        /** Places a template centred on (bx, bz) at the local ground height. */
        private boolean place(StructurePiecesBuilder out, String id, int bx, int bz, Rotation rot, boolean force) {
            Vec3i size = size(id);
            int[] rect = rect(bx, bz, size, rot, 0);
            int[] ys = {height(ctx, bx, bz), height(ctx, rect[0], rect[1]), height(ctx, rect[2], rect[1]),
                    height(ctx, rect[0], rect[3]), height(ctx, rect[2], rect[3])};
            int[] sorted = ys.clone();
            java.util.Arrays.sort(sorted);
            if (!force && (sorted[4] - sorted[0] > 9 || isWater(ctx, bx, ys[0], bz))) {
                return false;
            }
            int y = sorted[2];
            out.addPiece(new TemplatePiece(ctx.structureTemplateManager(), new ResourceLocation(id), bx, y, bz, rot));
            rects.add(rect(bx, bz, size, rot, 2));
            if (!force) {
                int[] front = rotate(0, -(size.getZ() / 2 + 2), rot);
                int fx = bx + front[0], fz = bz + front[1];
                if (ring.inside(bx, bz, 0)) {
                    doors.add(new int[]{fx, fz, ring.cx, ring.cz, 0});
                } else {
                    int[] g = nearestGate(bx, bz);
                    double ga = ring.angleOf(g[0], g[1]);
                    // aim just outside the gate
                    int ox = (int) Math.round(g[0] + Math.cos(ga) * 5), oz = (int) Math.round(g[1] + Math.sin(ga) * 5);
                    doors.add(new int[]{fx, fz, ox, oz, 1});
                }
            }
            return true;
        }

        private Vec3i size(String id) {
            StructureTemplate t = ctx.structureTemplateManager().getOrCreate(new ResourceLocation(id));
            return t.getSize();
        }

        private static int[] rect(int bx, int bz, Vec3i size, Rotation rot, int pad) {
            boolean swap = rot == Rotation.CLOCKWISE_90 || rot == Rotation.COUNTERCLOCKWISE_90;
            int sx = swap ? size.getZ() : size.getX(), sz = swap ? size.getX() : size.getZ();
            return new int[]{bx - sx / 2 - pad, bz - sz / 2 - pad, bx + (sx - 1) / 2 + pad + 1, bz + (sz - 1) / 2 + pad + 1};
        }

        private boolean overlaps(int[] r) {
            for (int[] o : rects) {
                if (r[0] <= o[2] && r[2] >= o[0] && r[1] <= o[3] && r[3] >= o[1]) {
                    return true;
                }
            }
            return false;
        }

        private boolean cornersInside(int[] r, double margin) {
            return ring.inside(r[0], r[1], margin) && ring.inside(r[2], r[1], margin)
                    && ring.inside(r[0], r[3], margin) && ring.inside(r[2], r[3], margin);
        }

        private boolean anyCornerInside(int[] r, double margin) {
            return ring.inside(r[0], r[1], margin) || ring.inside(r[2], r[1], margin)
                    || ring.inside(r[0], r[3], margin) || ring.inside(r[2], r[3], margin);
        }

        private boolean inAnyRect(int x, int z) {
            for (int[] o : rects) {
                if (x > o[0] + 1 && x < o[2] - 1 && z > o[1] + 1 && z < o[3] - 1) {
                    return true;
                }
            }
            return false;
        }

        /** Walks a path from (x, z) toward the plaza; stops at the plaza or on meeting another path. */
        private void road(int x0, int z0, int tx, int tz, int halfWidth, int plazaHalf) {
            double x = x0, z = z0;
            double wob = (rand.nextDouble() - 0.5) * 0.6;
            for (int step = 0; step < 160; step++) {
                int ix = (int) Math.round(x), iz = (int) Math.round(z);
                if (Math.abs(ix - tx) <= plazaHalf && Math.abs(iz - tz) <= plazaHalf) {
                    return;
                }
                if (halfWidth == 0 && step > 3 && (paths.contains(key(ix + 1, iz)) || paths.contains(key(ix - 1, iz))
                        || paths.contains(key(ix, iz + 1)) || paths.contains(key(ix, iz - 1)))) {
                    paths.add(key(ix, iz));
                    return;
                }
                for (int dx = -halfWidth; dx <= halfWidth; dx++) {
                    for (int dz = -halfWidth; dz <= halfWidth; dz++) {
                        if (!inAnyRect(ix + dx, iz + dz)) {
                            paths.add(key(ix + dx, iz + dz));
                        }
                    }
                }
                double ang = Math.atan2(tz - z, tx - x) + wob * Math.sin(step * 0.15);
                x += Math.cos(ang);
                z += Math.sin(ang);
            }
        }

        static long key(int x, int z) {
            return ((long) x << 32) | (z & 0xFFFFFFFFL);
        }

        static Rotation faceToward(int bx, int bz, int tx, int tz) {
            int dx = tx - bx, dz = tz - bz;
            if (Math.abs(dx) > Math.abs(dz)) {
                return dx > 0 ? Rotation.CLOCKWISE_90 : Rotation.COUNTERCLOCKWISE_90;
            }
            return dz > 0 ? Rotation.CLOCKWISE_180 : Rotation.NONE;
        }

        static int[] rotate(int dx, int dz, Rotation rot) {
            return switch (rot) {
                case CLOCKWISE_90 -> new int[]{-dz, dx};
                case CLOCKWISE_180 -> new int[]{-dx, -dz};
                case COUNTERCLOCKWISE_90 -> new int[]{dz, -dx};
                default -> new int[]{dx, dz};
            };
        }
    }
}
