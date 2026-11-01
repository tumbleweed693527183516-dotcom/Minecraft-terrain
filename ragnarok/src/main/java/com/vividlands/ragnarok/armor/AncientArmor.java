package com.vividlands.ragnarok.armor;

import com.vividlands.ragnarok.Ragnarok;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Armor of the ancient civilizations (AncientSets: Sumer and Egypt up to the Samurai and the Pharaoh), four pieces each,
 * in their own creative tab. Item ids: vividlands_ragnarok:<set>_helmet / _chestplate / _leggings / _boots.
 */
public final class AncientArmor {
    public static final Map<String, List<AncientArmorItem>> SETS = new LinkedHashMap<>();
    private static final String[] PIECE_NAMES = {"helmet", "chestplate", "leggings", "boots"};
    private static final ArmorItem.Type[] TYPES = {ArmorItem.Type.HELMET, ArmorItem.Type.CHESTPLATE, ArmorItem.Type.LEGGINGS, ArmorItem.Type.BOOTS};

    private AncientArmor() {
    }

    public static void register() {
        int n = AncientSets.ALL.size();
        for (int t = 0; t < n; t++) {
            AncientSets.Set set = AncientSets.ALL.get(t);
            AncientArmorMaterial mat = new AncientArmorMaterial(set, t + 1, n);
            double p = mat.progress();
            Rarity rarity = p < 0.34 ? Rarity.COMMON : p < 0.67 ? Rarity.UNCOMMON : p < 0.9 ? Rarity.RARE : Rarity.EPIC;
            List<AncientArmorItem> pieces = new ArrayList<>();
            for (int i = 0; i < 4; i++) {
                AncientArmorItem item = new AncientArmorItem(mat, TYPES[i], new Item.Properties().rarity(rarity));
                pieces.add(Registry.register(BuiltInRegistries.ITEM,
                        new ResourceLocation(Ragnarok.MOD_ID, set.id() + "_" + PIECE_NAMES[i]), item));
            }
            SETS.put(set.id(), pieces);
        }
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, new ResourceLocation(Ragnarok.MOD_ID, "ancient"),
                FabricItemGroup.builder()
                        .title(Component.translatable("itemGroup.vividlands_ragnarok.ancient"))
                        .icon(() -> new ItemStack(SETS.get("agamemnon").get(0)))
                        .displayItems((params, out) -> {
                            if (Glamour.TEMPLATE != null) out.accept(Glamour.TEMPLATE);
                            SETS.values().forEach(l -> l.forEach(out::accept));
                        })
                        .build());
    }
}
