package com.vividlands.ragnarok.client.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.mojang.blaze3d.vertex.PoseStack;
import com.vividlands.ragnarok.boss.Bosses;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Draws bosses bigger than the creature they are built on (scaled from their feet). Works for any mod's renderer. */
@Mixin(EntityRenderDispatcher.class)
public abstract class EntityRenderDispatcherMixin {
    @WrapOperation(method = "render", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/renderer/entity/EntityRenderer;render(Lnet/minecraft/world/entity/Entity;FFLcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;I)V"))
    private void vlr$scaleBoss(EntityRenderer<Entity> renderer, Entity entity, float yaw, float partialTick, PoseStack pose,
                               MultiBufferSource buffers, int light, Operation<Void> original) {
        float s = Bosses.scaleOf(entity);
        if (s == 1f) {
            original.call(renderer, entity, yaw, partialTick, pose, buffers, light);
            return;
        }
        pose.pushPose();
        pose.scale(s, s, s);
        original.call(renderer, entity, yaw, partialTick, pose, buffers, light);
        pose.popPose();
    }
}
