package com.vividlands.ragnarok.client.mixin;

import com.mojang.blaze3d.vertex.PoseStack;
import com.vividlands.ragnarok.armor.Glamour;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.Model;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import software.bernie.geckolib.animatable.client.RenderProvider;
import software.bernie.geckolib.renderer.GeoArmorRenderer;

/** Glamoured armour: draw the look piece's 3D model in place of the real piece (see armor/Glamour). */
@Mixin(value = HumanoidArmorLayer.class, priority = 900)
public abstract class HumanoidArmorLayerGlamourMixin<T extends LivingEntity, M extends HumanoidModel<T>, A extends HumanoidModel<T>> {
    @SuppressWarnings({"unchecked", "rawtypes"})
    @Inject(method = "renderArmorPiece", at = @At("HEAD"), cancellable = true)
    private void vlr$glamour(PoseStack poseStack, MultiBufferSource buffers, T entity, EquipmentSlot slot, int light, A baseModel,
                             CallbackInfo ci) {
        ItemStack worn = entity.getItemBySlot(slot);
        if (worn.isEmpty()) return;
        ItemStack look = Glamour.appearance(worn);
        if (look.isEmpty() || !(look.getItem() instanceof ArmorItem a) || a.getEquipmentSlot() != slot) return;
        Model model = RenderProvider.of(look).getGenericArmorModel(entity, look, slot, (HumanoidModel<LivingEntity>) (HumanoidModel) baseModel);
        if (!(model instanceof GeoArmorRenderer<?> geo)) return;
        geo.prepForRender(entity, look, slot, baseModel);
        ((HumanoidModel) baseModel).copyPropertiesTo((HumanoidModel) geo);
        geo.renderToBuffer(poseStack, null, light, OverlayTexture.NO_OVERLAY, 1, 1, 1, 1);
        ci.cancel();
    }
}
