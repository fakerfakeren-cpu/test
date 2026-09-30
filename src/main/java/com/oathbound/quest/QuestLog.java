package com.oathbound.quest;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.oathbound.Oathbound;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModTags;
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
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.levelgen.structure.Structure;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

/**
 * The Path: the Lantern Chronicle's quests, and how the Order pays its squire.
 * <ul>
 *   <li>Completion is tracked by {@code oathbound:quests/*} advancements (item, kill and location triggers in
 *       data, plus criteria granted from code for puzzles and rites).</li>
 *   <li><b>Tithes</b>: each quest's reward is owed until the player warms their hands at any kindled Wayshrine,
 *       where every owed tithe rises from the fire at once ({@code oathbound:claimed/*} marks payment).</li>
 *   <li><b>Boons</b>: finishing a chapter's main quests lets the player swear one of three permanent Oath Boons
 *       from the Chronicle ({@code oathbound:boons/*}).</li>
 * </ul>
 * The server mirrors each player's state onto their Chronicle item so the screen can read it without custom
 * networking; choosing a boon runs {@code /oathchronicle boon <id>}.
 */
public final class QuestLog {
    /** Chapter ids; titles/lore are lang keys chronicle.oathbound.chapter.N[.title|.lore]. */
    public static final int CHAPTERS = 7;

    public record Reward(Supplier<? extends ItemLike> item, int count) {
        public ItemStack stack() {
            return new ItemStack(item.get(), count);
        }
    }

    public record Quest(String id, int chapter, String parent, Supplier<? extends ItemLike> icon, int xp, boolean main, List<Reward> rewards) {
        public ItemStack iconStack() {
            return new ItemStack(icon.get());
        }
    }

    /** Where the Warden's Lantern points next. */
    public record Destination(TagKey<Structure> structure, String label) {}

    public static final Map<String, Quest> QUESTS = new LinkedHashMap<>();

    static {
        // I. The Last Squire
        q("root", 0, null, ModItems.LANTERN_CHRONICLE, 0, true, r(ModItems.WAYFARERS_BREAD, 6), r(() -> Items.TORCH, 16));
        q("lumenite", 0, "root", ModItems.LUMENITE_SHARD, 15, true, r(() -> Items.IRON_INGOT, 3));
        q("oathsteel", 0, "lumenite", ModItems.OATHSTEEL_INGOT, 25, true, r(ModItems.LUMENITE_SHARD, 3));
        q("lantern", 0, "oathsteel", ModItems.WARDENS_LANTERN, 30, true, r(ModItems.LUMENITE_SHARD, 4));
        q("wayshrine", 0, "lantern", ModBlocks.WAYSHRINE_BRAZIER, 40, true, r(ModItems.HONEYED_MEAD, 2), r(ModItems.LUMEN_FLASK, 2));
        q("oathsteel_arms", 0, "oathsteel", ModItems.OATHSTEEL_LONGSWORD, 30, false, r(ModItems.KNIGHTS_STEW, 1));
        q("oathsteel_armor", 0, "oathsteel", ModItems.OATHSTEEL_CHESTPLATE, 40, false, r(() -> Items.GOLDEN_APPLE, 1));
        // II. Where the Bells Drown
        q("chapel", 1, "wayshrine", ModBlocks.CHAPEL_BELL, 40, true, r(ModItems.HONEYED_MEAD, 1));
        q("hymn", 1, "chapel", ModBlocks.HYMN_STONE, 60, true, r(ModItems.LUMEN_FLASK, 3));
        q("caldris", 1, "hymn", ModItems.SEAL_OF_VALOR, 150, true, r(() -> Items.GOLDEN_APPLE, 2), r(ModItems.OATHSTEEL_INGOT, 2));
        q("anchor", 1, "caldris", ModItems.DROWNED_ANCHOR, 40, false, r(() -> Items.EXPERIENCE_BOTTLE, 6));
        // III. The Hollow Spire
        q("spire", 2, "caldris", ModBlocks.RUNE_DIAL, 50, true, r(ModItems.KNIGHTS_STEW, 1));
        q("spellsilk", 2, "spire", ModItems.SPELLSILK, 30, false, r(ModItems.SPELLSILK, 2));
        q("cipher", 2, "spire", ModBlocks.CIPHER_LECTERN, 80, true, r(ModItems.LUMEN_FLASK, 3), r(() -> Items.GOLDEN_APPLE, 1));
        q("veyl", 2, "cipher", ModItems.SEAL_OF_WISDOM, 200, true, r(() -> Items.DIAMOND, 3), r(() -> Items.EXPERIENCE_BOTTLE, 8));
        q("arcanist", 2, "spellsilk", ModItems.ARCANIST_ROBE, 60, false, r(ModItems.SPELLSILK, 2));
        q("dawnstring", 2, "spellsilk", ModItems.DAWNSTRING_LONGBOW, 60, false, r(() -> Items.ARROW, 32));
        // IV. The Barrow of Kings
        q("barrow", 3, "veyl", ModBlocks.SARCOPHAGUS, 60, true, r(ModItems.KNIGHTS_STEW, 1), r(() -> Items.TORCH, 16));
        q("honest_king", 3, "barrow", ModBlocks.BARROW_SEAL, 100, true, r(() -> Items.GOLDEN_APPLE, 2));
        q("hrodgar", 3, "honest_king", ModItems.SEAL_OF_SACRIFICE, 250, true, r(() -> Items.DIAMOND, 4), r(() -> Items.EXPERIENCE_BOTTLE, 10));
        q("warhorn", 3, "hrodgar", ModItems.HOUSECARL_WARHORN, 50, false, r(ModItems.HONEYED_MEAD, 3));
        // V. The Sundered Gate
        q("oathkey", 4, "hrodgar", ModItems.OATHKEY, 100, true, r(ModItems.ELIXIR_OF_DAWN, 2));
        q("citadel", 4, "oathkey", ModBlocks.SUNDERED_KEYSTONE, 80, true, r(ModItems.LUMENITE_SHARD, 8));
        q("gate", 4, "citadel", ModBlocks.WARDSTONE_PILLAR, 120, true, r(ModItems.ELIXIR_OF_DAWN, 1), r(() -> Items.GOLDEN_APPLE, 2));
        q("gloaming", 4, "gate", ModBlocks.GLOAM_MOSS, 100, true, r(ModItems.LUMEN_FLASK, 4));
        // VI. The Hollow Crown
        q("sickle", 5, "gloaming", ModItems.SHADOWREAP_SICKLE, 80, false, r(ModItems.GLOAM_ESSENCE, 4));
        q("veilhound", 5, "gloaming", ModItems.GLOAM_ESSENCE, 60, false, r(ModItems.KNIGHTS_STEW, 2));
        q("throne", 5, "gloaming", ModBlocks.WARD_LANTERN, 100, true, r(() -> Items.GOLDEN_APPLE, 2));
        q("morvane", 5, "throne", ModItems.EVERFLAME_EMBER, 500, true, r(() -> Items.ENCHANTED_GOLDEN_APPLE, 1), r(() -> Items.DIAMOND_BLOCK, 2));
        q("dawnbreaker", 5, "morvane", ModItems.DAWNBREAKER, 100, false, r(() -> Items.EXPERIENCE_BOTTLE, 16));
        q("crown", 5, "morvane", ModItems.HOLLOW_CROWN, 100, false, r(() -> Items.EXPERIENCE_BOTTLE, 16));
        // VII. Tales and Secrets (side quests)
        q("gloamling", 6, "root", ModItems.GLOAM_ESSENCE, 30, false, r(ModItems.LUMENITE_SHARD, 2));
        q("lanternmoth", 6, "root", ModItems.LUMINOUS_DUST, 20, false, r(() -> Items.GLOW_BERRIES, 8));
        q("elixir", 6, "lanternmoth", ModItems.ELIXIR_OF_DAWN, 40, false, r(ModItems.LUMINOUS_DUST, 4));
        q("flask", 6, "lanternmoth", ModItems.LUMEN_FLASK, 20, false, r(ModItems.LUMEN_FLASK, 2));
        q("forsworn", 6, "root", ModItems.OATHSTEEL_HELMET, 60, false, r(() -> Items.GOLDEN_APPLE, 1));
        q("insignia", 6, "root", ModItems.LANTERNGUARD_INSIGNIA, 60, false, r(() -> Items.EMERALD, 8));
        q("loremaster", 6, "root", ModBlocks.LORE_TABLET, 150, false, r(() -> Items.ENCHANTED_BOOK, 1), r(() -> Items.EXPERIENCE_BOTTLE, 12));
        q("everflame", 6, "morvane", ModItems.EVERFLAME_LANTERN, 200, false, r(() -> Items.NETHER_STAR, 1));
        // the places off the Path
        q("grove_king", 6, "root", ModItems.GROVE_KINGS_CROWN, 150, false, r(() -> Items.GOLDEN_APPLE, 2), r(ModItems.ELIXIR_OF_THE_WAYFARER, 2));
        q("bog_mother", 6, "root", ModItems.BOG_MOTHERS_LANTERN, 150, false, r(() -> Items.GOLDEN_APPLE, 2), r(ModItems.ELIXIR_OF_SHROUDS, 2));
        q("cinder_colossus", 6, "root", ModItems.CINDER_HEART, 200, false, r(() -> Items.DIAMOND, 3), r(ModItems.ELIXIR_OF_VALOR, 2));
        q("last_watch", 6, "root", ModBlocks.OATHSTEEL_LANTERN, 40, false, r(ModItems.TRAIL_RATIONS, 4));
        q("tideglass", 6, "root", ModBlocks.BARNACLED_TIDESTONE_BRICKS, 40, false, r(ModItems.ELIXIR_OF_TIDES, 2));
        q("delve", 6, "root", ModBlocks.LUMENITE_ORE, 40, false, r(ModItems.LUMENITE_SHARD, 8));
        q("star_readers", 6, "root", ModBlocks.GLOAMGLASS, 60, false, r(ModItems.SPELLSILK, 3));
    }

    private static Reward r(Supplier<? extends ItemLike> item, int count) {
        return new Reward(item, count);
    }

    private static void q(String id, int chapter, String parent, Supplier<? extends ItemLike> icon, int xp, boolean main, Reward... rewards) {
        QUESTS.put(id, new Quest(id, chapter, parent, icon, xp, main, List.of(rewards)));
    }

    public static Identifier questAdvancement(String id) {
        return Identifier.fromNamespaceAndPath(Oathbound.MODID, "quests/" + id);
    }

    public static Identifier claimedAdvancement(String id) {
        return Identifier.fromNamespaceAndPath(Oathbound.MODID, "claimed/" + id);
    }

    // ------------------------------------------------------------------ server side

    private static AdvancementHolder holder(ServerPlayer player, Identifier id) {
        return player.level().getServer().getAdvancements().get(id);
    }

    private static boolean isDone(ServerPlayer player, Identifier id) {
        AdvancementHolder holder = holder(player, id);
        return holder != null && player.getAdvancements().getOrStartProgress(holder).isDone();
    }

    public static boolean isComplete(ServerPlayer player, String quest) {
        return isDone(player, questAdvancement(quest));
    }

    public static boolean isClaimed(ServerPlayer player, String quest) {
        return isDone(player, claimedAdvancement(quest));
    }

    /** Awards a code-driven criterion (puzzles, rites). Safe to call repeatedly. */
    public static void grant(ServerPlayer player, String quest, String criterion) {
        AdvancementHolder holder = holder(player, questAdvancement(quest));
        if (holder == null) {
            Oathbound.LOGGER.warn("Missing quest advancement {}", quest);
            return;
        }
        if (player.getAdvancements().award(holder, criterion)) {
            player.level().playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.QUEST_COMPLETE.get(), SoundSource.PLAYERS, 0.7f, 1.0f);
        }
    }

    public static void readTablet(ServerPlayer player, int index) {
        grant(player, "loremaster", "tablet_" + index);
    }

    /** The next structure the Chronicle wants the player to find, in story order. */
    public static Destination nextDestination(ServerPlayer player) {
        if (!isComplete(player, "wayshrine")) return new Destination(ModTags.WAYSHRINE, "wayshrine");
        if (!isComplete(player, "caldris")) return new Destination(ModTags.DROWNED_CHAPEL, "chapel");
        if (!isComplete(player, "veyl")) return new Destination(ModTags.ARCANIST_SPIRE, "spire");
        if (!isComplete(player, "hrodgar")) return new Destination(ModTags.BARROW, "barrow");
        if (!isComplete(player, "morvane")) return new Destination(ModTags.SUNDERED_CITADEL, "citadel");
        return null;
    }

    /** Writes the player's quest state onto a Chronicle stack. Only touches the stack when something changed. */
    public static void sync(ServerPlayer player, ItemStack book) {
        List<String> done = new ArrayList<>(), claimed = new ArrayList<>();
        for (String id : QUESTS.keySet()) {
            if (isComplete(player, id)) done.add(id);
            if (isClaimed(player, id)) claimed.add(id);
        }
        List<String> boons = new ArrayList<>();
        for (Boon b : BOONS) if (hasBoon(player, b.id())) boons.add(b.id());
        String d = String.join(",", done), c = String.join(",", claimed), bo = String.join(",", boons);
        CompoundTag current = book.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        if (d.equals(current.getStringOr("done", "-")) && c.equals(current.getStringOr("paid", "-")) && bo.equals(current.getStringOr("boons", "-"))) return;
        CustomData.update(DataComponents.CUSTOM_DATA, book, tag -> {
            tag.putString("done", d);
            tag.putString("paid", c);
            tag.putString("boons", bo);
        });
    }

    public static void syncAll(ServerPlayer player) {
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(ModItems.LANTERN_CHRONICLE.get())) sync(player, s);
        }
    }

    // ------------------------------------------------------------------ tithes (quest rewards)
    /** Quests whose tithe is owed: complete but not yet paid. */
    public static List<Quest> owedTithes(ServerPlayer player) {
        List<Quest> out = new ArrayList<>();
        for (Quest q : QUESTS.values()) if (isComplete(player, q.id()) && !isClaimed(player, q.id())) out.add(q);
        return out;
    }

    /**
     * Pays every owed tithe at a kindled Wayshrine: the items rise out of the brazier's fire one by one.
     * Returns the number of tithes paid.
     */
    public static int payTithes(ServerPlayer player, net.minecraft.core.BlockPos brazier) {
        List<Quest> owed = owedTithes(player);
        if (owed.isEmpty()) return 0;
        var level = (net.minecraft.server.level.ServerLevel) player.level();
        int delay = 0;
        int xp = 0;
        for (Quest q : owed) {
            AdvancementHolder marker = holder(player, claimedAdvancement(q.id()));
            if (marker == null) continue;
            player.getAdvancements().award(marker, "claimed");
            xp += q.xp();
            for (Reward reward : q.rewards()) {
                ItemStack stack = reward.stack();
                com.oathbound.util.Scheduler.later(level, 4 + delay, l -> {
                    net.minecraft.world.phys.Vec3 at = net.minecraft.world.phys.Vec3.atCenterOf(brazier).add(0, 0.9, 0);
                    var item = new net.minecraft.world.entity.item.ItemEntity(l, at.x, at.y, at.z, stack);
                    item.setDeltaMovement((l.getRandom().nextDouble() - 0.5) * 0.12, 0.32, (l.getRandom().nextDouble() - 0.5) * 0.12);
                    item.setPickUpDelay(10);
                    l.addFreshEntity(item);
                    com.oathbound.util.Vfx.burst(l, com.oathbound.registry.ModParticles.EMBER.get(), at, 12, 0.2, 0.08);
                    l.playSound(null, brazier, com.oathbound.registry.ModSounds.LANTERN_IGNITE.get(), SoundSource.BLOCKS, 0.7f, 1.4f);
                });
                delay += 5;
            }
        }
        if (xp > 0) player.giveExperiencePoints(xp);
        level.playSound(null, brazier, ModSounds.QUEST_COMPLETE.get(), SoundSource.BLOCKS, 1.0f, 1.0f);
        player.sendSystemMessage(Component.translatable("chronicle.oathbound.tithe.paid", owed.size()).withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
        syncAll(player);
        return owed.size();
    }

    // ------------------------------------------------------------------ boons (chapter rewards)
    public record Boon(String id, int chapter, Supplier<? extends ItemLike> icon) {}

    public static final List<Boon> BOONS = new ArrayList<>();

    static {
        b("squires_vigor", 0, () -> Items.GOLDEN_APPLE);
        b("lamplighters_thrift", 0, ModItems.WARDENS_LANTERN);
        b("pilgrims_stride", 0, () -> Items.LEATHER_BOOTS);
        b("tidebound", 1, () -> Items.HEART_OF_THE_SEA);
        b("knights_guard", 1, () -> Items.SHIELD);
        b("long_reach", 1, ModItems.DROWNED_ANCHOR);
        b("arcane_insight", 2, ModItems.STAFF_OF_VEYL);
        b("scholars_luck", 2, () -> Items.RABBIT_FOOT);
        b("glyphskin", 2, ModItems.SPELLSILK);
        b("oath_of_the_housecarl", 3, ModItems.HOUSECARL_WARHORN);
        b("kingsblood", 3, () -> Items.GOLDEN_CHESTPLATE);
        b("grave_sight", 3, () -> Items.ENDER_EYE);
        b("veilwalker", 4, ModBlocks.GLOAM_MOSS);
        b("gatesworn", 4, ModItems.OATHKEY);
        b("featherfall", 4, () -> Items.FEATHER);
        b("everflame_heart", 5, ModItems.EVERFLAME_EMBER);
        b("kingslayer", 5, ModItems.DAWNBREAKER);
        b("dawnbound", 5, () -> Items.SUNFLOWER);
    }

    private static void b(String id, int chapter, Supplier<? extends ItemLike> icon) {
        BOONS.add(new Boon(id, chapter, icon));
    }

    public static Identifier boonAdvancement(String id) {
        return Identifier.fromNamespaceAndPath(Oathbound.MODID, "boons/" + id);
    }

    public static boolean hasBoon(ServerPlayer player, String id) {
        return isDone(player, boonAdvancement(id));
    }

    public static boolean chapterComplete(ServerPlayer player, int chapter) {
        boolean any = false;
        for (Quest q : QUESTS.values()) {
            if (q.chapter() != chapter || !q.main()) continue;
            any = true;
            if (!isComplete(player, q.id())) return false;
        }
        return any;
    }

    public static String chosenBoon(ServerPlayer player, int chapter) {
        for (Boon b : BOONS) if (b.chapter() == chapter && hasBoon(player, b.id())) return b.id();
        return null;
    }

    public static int chooseBoon(ServerPlayer player, String id) {
        Boon boon = null;
        for (Boon b : BOONS) if (b.id().equals(id)) boon = b;
        if (boon == null) {
            player.sendSystemMessage(Component.translatable("chronicle.oathbound.boon.unknown").withStyle(ChatFormatting.RED));
            return 0;
        }
        if (!chapterComplete(player, boon.chapter())) {
            player.sendSystemMessage(Component.translatable("chronicle.oathbound.boon.locked").withStyle(ChatFormatting.RED));
            return 0;
        }
        if (chosenBoon(player, boon.chapter()) != null) {
            player.sendSystemMessage(Component.translatable("chronicle.oathbound.boon.already").withStyle(ChatFormatting.GRAY));
            return 0;
        }
        AdvancementHolder h = holder(player, boonAdvancement(id));
        if (h == null) return 0;
        player.getAdvancements().award(h, "sworn");
        var level = (net.minecraft.server.level.ServerLevel) player.level();
        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.PUZZLE_SOLVED.get(), SoundSource.PLAYERS, 1.0f, 1.3f);
        com.oathbound.util.Vfx.sphere(level, com.oathbound.registry.ModParticles.SUNBURST.get(), player.position().add(0, 1, 0), 1.6, 60);
        player.sendSystemMessage(Component.translatable("chronicle.oathbound.boon.sworn",
            Component.translatable("boon.oathbound." + id + ".title").withStyle(ChatFormatting.GOLD)).withStyle(ChatFormatting.YELLOW, ChatFormatting.ITALIC));
        syncAll(player);
        return 1;
    }

    /** {@code /oathchronicle boon <id>}: needs no permission; a player can only swear their own boons. */
    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("oathchronicle")
            .then(Commands.literal("boon")
                .then(Commands.argument("boon", StringArgumentType.word())
                    .suggests((c, b) -> SharedSuggestionProvider.suggest(BOONS.stream().map(Boon::id), b))
                    .executes(c -> chooseBoon(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "boon"))))));
    }

    private QuestLog() {}
}
