package com.rimeheart.quest;

import com.rimeheart.Rimeheart;
import com.rimeheart.registry.ModBlocks;
import com.rimeheart.registry.ModItems;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.ChatFormatting;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.ItemLike;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

/**
 * The Warden's Journal quest line. Completion is tracked by the {@code rimeheart:quests/*} advancements;
 * rewards are claimed from the journal GUI (which runs {@code /rimejournal claim <quest>}) and the claim is
 * remembered with a hidden {@code rimeheart:claimed/<quest>} advancement, so it survives relogs and works on
 * dedicated servers without any custom networking. The server mirrors each player's quest state onto their
 * journal item (custom data) so the client-side screen can show it.
 */
public final class QuestLog {
    public static final String[] CHAPTERS = {"0", "1", "2", "3", "4"};

    public record Reward(Supplier<? extends ItemLike> item, int count) {
        public ItemStack stack() {
            return new ItemStack(item.get(), count);
        }
    }

    public record Quest(String id, int chapter, String parent, Supplier<? extends ItemLike> icon, int xp, List<Reward> rewards) {
        public ItemStack iconStack() {
            return new ItemStack(icon.get());
        }
    }

    public static final Map<String, Quest> QUESTS = new LinkedHashMap<>();

    static {
        // Chapter 0: First Frost
        q("root", 0, null, ModItems.WARDENS_JOURNAL, 0, r(() -> Items.TORCH, 16), r(() -> Items.BREAD, 6));
        q("frostiron", 0, "root", ModItems.RAW_FROSTIRON, 20, r(() -> Items.COAL, 12));
        q("ingot", 0, "frostiron", ModItems.FROSTIRON_INGOT, 25, r(() -> Items.BREAD, 8));
        q("pickaxe", 0, "ingot", ModItems.FROSTIRON_PICKAXE, 30, r(ModItems.FROSTIRON_INGOT, 2));
        q("frostiron_armor", 0, "ingot", ModItems.FROSTIRON_CHESTPLATE, 60, r(ModItems.FROSTIRON_INGOT, 3), r(() -> Items.GOLDEN_APPLE, 1));
        q("hearthfire", 0, "root", ModItems.HEARTHFIRE_STEW, 20, r(() -> Items.BAKED_POTATO, 6));
        // Chapter 1: Rime and Crystal
        q("rime_shard", 1, "frostiron", ModItems.RIME_SHARD, 20, r(ModItems.FROST_CHARGE, 2));
        q("frost_charge", 1, "rime_shard", ModItems.FROST_CHARGE, 20, r(() -> Items.GUNPOWDER, 4));
        q("rimebow", 1, "rime_shard", ModItems.RIMEBOW, 40, r(ModItems.FROSTIRON_INGOT, 2));
        q("glacier_maul", 1, "rime_shard", ModItems.GLACIER_MAUL, 50, r(() -> Items.GOLDEN_APPLE, 1));
        // Chapter 2: Things in the Snow
        q("wraith", 2, "frostiron", ModItems.WRAITH_ESSENCE, 40, r(ModItems.HEARTHFIRE_STEW, 1));
        q("shardling", 2, "rime_shard", ModBlocks.RIME_CRYSTAL_CLUSTER, 30, r(ModItems.RIME_SHARD, 4));
        q("frostbite_blade", 2, "wraith", ModItems.FROSTBITE_BLADE, 50, r(ModItems.WRAITH_ESSENCE, 2));
        q("wraithweave", 2, "wraith", ModItems.WRAITHWEAVE_ROBE, 80, r(() -> Items.DIAMOND, 2));
        q("blizzard_staff", 2, "wraith", ModItems.BLIZZARD_STAFF, 60, r(ModItems.FROST_CHARGE, 4));
        // Chapter 3: The Frozen Sanctum
        q("sanctum", 3, "frostiron", ModBlocks.CHISELED_RIMESTONE_BRICKS, 80, r(() -> Items.COOKED_BEEF, 8), r(ModBlocks.FROST_LAMP, 2));
        q("vault", 3, "sanctum", ModItems.GLACIAL_HEART, 100, r(() -> Items.GOLDEN_APPLE, 1), r(ModItems.RIME_SHARD, 4));
        q("winter_horn", 3, "vault", ModItems.WINTER_HORN, 100, r(() -> Items.GOLDEN_APPLE, 3), r(ModItems.HEARTHFIRE_STEW, 1));
        // Chapter 4: The Long Winter
        q("sovereign", 4, "winter_horn", ModItems.SOVEREIGN_CORE, 300, r(() -> Items.DIAMOND, 2), r(() -> Items.EXPERIENCE_BOTTLE, 16));
        q("winterfang", 4, "sovereign", ModItems.WINTERFANG, 150, r(() -> Items.EXPERIENCE_BOTTLE, 16));
    }

    private static Reward r(Supplier<? extends ItemLike> item, int count) {
        return new Reward(item, count);
    }

    private static void q(String id, int chapter, String parent, Supplier<? extends ItemLike> icon, int xp, Reward... rewards) {
        QUESTS.put(id, new Quest(id, chapter, parent, icon, xp, List.of(rewards)));
    }

    public static Identifier questAdvancement(String id) {
        return Identifier.fromNamespaceAndPath(Rimeheart.MODID, "quests/" + id);
    }

    public static Identifier claimedAdvancement(String id) {
        return Identifier.fromNamespaceAndPath(Rimeheart.MODID, "claimed/" + id);
    }

    // ------------------------------------------------------------------ server side

    private static boolean isDone(ServerPlayer player, Identifier id) {
        AdvancementHolder holder = player.level().getServer().getAdvancements().get(id);
        return holder != null && player.getAdvancements().getOrStartProgress(holder).isDone();
    }

    public static boolean isComplete(ServerPlayer player, String quest) {
        return isDone(player, questAdvancement(quest));
    }

    public static boolean isClaimed(ServerPlayer player, String quest) {
        return isDone(player, claimedAdvancement(quest));
    }

    /** Writes the player's quest state onto a journal stack. Only touches the stack when something changed. */
    public static void sync(ServerPlayer player, ItemStack journal) {
        List<String> done = new ArrayList<>(), claimed = new ArrayList<>();
        for (String id : QUESTS.keySet()) {
            if (isComplete(player, id)) done.add(id);
            if (isClaimed(player, id)) claimed.add(id);
        }
        String d = String.join(",", done), c = String.join(",", claimed);
        CompoundTag current = journal.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        if (d.equals(current.getStringOr("quests_done", "-")) && c.equals(current.getStringOr("quests_claimed", "-"))) return;
        CustomData.update(DataComponents.CUSTOM_DATA, journal, tag -> {
            tag.putString("quests_done", d);
            tag.putString("quests_claimed", c);
        });
    }

    private static void syncAll(ServerPlayer player) {
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(ModItems.WARDENS_JOURNAL.get())) sync(player, s);
        }
    }

    public static int claim(ServerPlayer player, String id) {
        Quest quest = QUESTS.get(id);
        if (quest == null) {
            player.sendSystemMessage(Component.translatable("journal.rimeheart.claim.unknown").withStyle(ChatFormatting.RED));
            return 0;
        }
        if (!isComplete(player, id)) {
            player.sendSystemMessage(Component.translatable("journal.rimeheart.claim.not_ready").withStyle(ChatFormatting.RED));
            return 0;
        }
        AdvancementHolder marker = player.level().getServer().getAdvancements().get(claimedAdvancement(id));
        if (marker == null || player.getAdvancements().getOrStartProgress(marker).isDone()) {
            player.sendSystemMessage(Component.translatable("journal.rimeheart.claim.already").withStyle(ChatFormatting.GRAY));
            return 0;
        }
        player.getAdvancements().award(marker, "claimed");
        for (Reward reward : quest.rewards()) {
            ItemStack stack = reward.stack();
            if (!player.getInventory().add(stack) && !stack.isEmpty()) player.drop(stack, false);
        }
        if (quest.xp() > 0) player.giveExperiencePoints(quest.xp());
        player.level().playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.6f, 1.4f);
        player.sendSystemMessage(Component.translatable("journal.rimeheart.claim.done",
            Component.translatable("quest.rimeheart." + id + ".title").withStyle(ChatFormatting.GOLD)).withStyle(ChatFormatting.LIGHT_PURPLE));
        syncAll(player);
        return 1;
    }

    /** {@code /rimejournal claim <quest>}: needs no permission; players can only claim their own finished quests. */
    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("rimejournal")
            .then(Commands.literal("claim")
                .then(Commands.argument("quest", StringArgumentType.word())
                    .suggests((c, b) -> SharedSuggestionProvider.suggest(QUESTS.keySet(), b))
                    .executes(c -> claim(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "quest"))))));
    }

    private QuestLog() {}
}
