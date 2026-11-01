package com.vividlands.ragnarok.armor;

import com.google.gson.JsonObject;
import com.vividlands.ragnarok.Ragnarok;
import net.minecraft.ChatFormatting;
import net.minecraft.core.NonNullList;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Container;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.CustomRecipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.SimpleCraftingRecipeSerializer;
import net.minecraft.world.item.crafting.SmithingRecipe;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoItem;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Transmogrification ("glamour"): any armour piece can take on the look of one of the pack's 3D armour pieces while
 * keeping its own stats, enchantments and durability.
 *  - Smithing table: Glamour Template + your armour piece + the piece whose look you want (same slot) -> your piece,
 *    now looking like the other one. The look piece and the template are used up.
 *  - Crafting grid: a glamoured piece on its own -> the same piece with its own look back.
 * The look is stored on the item as the NBT string "VividGlamour" (an item id); the client draws that item's model
 * instead (client/mixin/HumanoidArmorLayerGlamourMixin).
 */
public final class Glamour {
    public static final String TAG = "VividGlamour";
    public static Item TEMPLATE;
    private static final Map<Item, ItemStack> LOOKS = new HashMap<>();

    private Glamour() {
    }

    /** An armour piece that can lend its look: one of the pack's own 3D pieces. */
    public static boolean isLook(ItemStack s) {
        return s.getItem() instanceof ArmorItem && s.getItem() instanceof GeoItem;
    }

    /** The look a piece wears (an item stack to draw instead), or EMPTY. */
    public static ItemStack appearance(ItemStack stack) {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(TAG)) return ItemStack.EMPTY;
        Item item = BuiltInRegistries.ITEM.get(new ResourceLocation(tag.getString(TAG)));
        if (item == Items.AIR) return ItemStack.EMPTY;
        return LOOKS.computeIfAbsent(item, ItemStack::new);
    }

    public static void addTooltip(ItemStack stack, List<Component> lines) {
        ItemStack look = appearance(stack);
        if (!look.isEmpty()) {
            lines.add(1, Component.translatable("tooltip.vividlands_ragnarok.glamour", look.getHoverName())
                    .withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.ITALIC));
        }
    }

    // ------------------------------------------------------------------ smithing: apply a look
    public static final class Apply implements SmithingRecipe {
        private final ResourceLocation id;

        Apply(ResourceLocation id) {
            this.id = id;
        }

        @Override
        public boolean isTemplateIngredient(ItemStack s) {
            return s.is(TEMPLATE);
        }

        @Override
        public boolean isBaseIngredient(ItemStack s) {
            return s.getItem() instanceof ArmorItem;
        }

        @Override
        public boolean isAdditionIngredient(ItemStack s) {
            return isLook(s);
        }

        @Override
        public boolean matches(Container c, Level level) {
            ItemStack t = c.getItem(0), base = c.getItem(1), look = c.getItem(2);
            return isTemplateIngredient(t) && base.getItem() instanceof ArmorItem b && isLook(look)
                    && ((ArmorItem) look.getItem()).getEquipmentSlot() == b.getEquipmentSlot() && base.getItem() != look.getItem();
        }

        @Override
        public ItemStack assemble(Container c, RegistryAccess access) {
            ItemStack out = c.getItem(1).copy();
            out.getOrCreateTag().putString(TAG, BuiltInRegistries.ITEM.getKey(c.getItem(2).getItem()).toString());
            return out;
        }

        @Override
        public ItemStack getResultItem(RegistryAccess access) {
            return new ItemStack(TEMPLATE);
        }

        @Override
        public ResourceLocation getId() {
            return id;
        }

        @Override
        public RecipeSerializer<?> getSerializer() {
            return APPLY;
        }
    }

    public static final RecipeSerializer<Apply> APPLY = new RecipeSerializer<>() {
        @Override
        public Apply fromJson(ResourceLocation id, JsonObject json) {
            return new Apply(id);
        }

        @Override
        public Apply fromNetwork(ResourceLocation id, FriendlyByteBuf buf) {
            return new Apply(id);
        }

        @Override
        public void toNetwork(FriendlyByteBuf buf, Apply recipe) {
        }
    };

    // ------------------------------------------------------------------ crafting: take the look off
    public static final class Remove extends CustomRecipe {
        public Remove(ResourceLocation id, CraftingBookCategory category) {
            super(id, category);
        }

        private static ItemStack single(CraftingContainer c) {
            ItemStack found = ItemStack.EMPTY;
            for (int i = 0; i < c.getContainerSize(); i++) {
                ItemStack s = c.getItem(i);
                if (s.isEmpty()) continue;
                if (!found.isEmpty()) return ItemStack.EMPTY;
                found = s;
            }
            return found;
        }

        @Override
        public boolean matches(CraftingContainer c, Level level) {
            ItemStack s = single(c);
            return !s.isEmpty() && s.getTag() != null && s.getTag().contains(TAG);
        }

        @Override
        public ItemStack assemble(CraftingContainer c, RegistryAccess access) {
            ItemStack out = single(c).copy();
            out.getOrCreateTag().remove(TAG);
            if (out.getTag() != null && out.getTag().isEmpty()) out.setTag(null);
            return out;
        }

        @Override
        public NonNullList<ItemStack> getRemainingItems(CraftingContainer c) {
            return NonNullList.withSize(c.getContainerSize(), ItemStack.EMPTY);
        }

        @Override
        public boolean canCraftInDimensions(int w, int h) {
            return w * h >= 1;
        }

        @Override
        public RecipeSerializer<?> getSerializer() {
            return REMOVE;
        }
    }

    public static final RecipeSerializer<Remove> REMOVE = new SimpleCraftingRecipeSerializer<>(Remove::new);

    public static void register() {
        TEMPLATE = Registry.register(BuiltInRegistries.ITEM, new ResourceLocation(Ragnarok.MOD_ID, "glamour_template"),
                new Item(new Item.Properties().rarity(Rarity.RARE)));
        Registry.register(BuiltInRegistries.RECIPE_SERIALIZER, new ResourceLocation(Ragnarok.MOD_ID, "glamour"), APPLY);
        Registry.register(BuiltInRegistries.RECIPE_SERIALIZER, new ResourceLocation(Ragnarok.MOD_ID, "glamour_removal"), REMOVE);
    }
}
