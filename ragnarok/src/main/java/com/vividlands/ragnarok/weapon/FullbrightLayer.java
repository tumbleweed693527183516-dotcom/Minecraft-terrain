package com.vividlands.ragnarok.weapon;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

/**
 * Draws the glowing parts (texture "<name>_glow.png", transparent elsewhere) a second time at full brightness.
 * Unlike GeckoLib's emissive layer it needs no special shader, so the molten core glows with or without shader
 * packs and keeps the base texture untouched.
 */
final class FullbrightLayer<T extends GeoAnimatable> extends GeoRenderLayer<T> {
    private static final int FULL_BRIGHT = 0xF000F0;
    private final ResourceLocation glowTexture;

    FullbrightLayer(GeoRenderer<T> renderer, ResourceLocation glowTexture) {
        super(renderer);
        this.glowTexture = glowTexture;
    }

    @Override
    public void render(PoseStack poseStack, T animatable, BakedGeoModel bakedModel, RenderType renderType,
                       MultiBufferSource bufferSource, VertexConsumer buffer, float partialTick, int packedLight,
                       int packedOverlay) {
        RenderType glow = RenderType.entityCutoutNoCull(glowTexture);
        getRenderer().reRender(bakedModel, poseStack, bufferSource, animatable, glow, bufferSource.getBuffer(glow),
                partialTick, FULL_BRIGHT, packedOverlay, 1f, 1f, 1f, 1f);
    }
}
