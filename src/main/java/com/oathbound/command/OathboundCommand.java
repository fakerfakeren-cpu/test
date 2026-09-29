package com.oathbound.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.oathbound.entity.boss.KeeperEntity;
import com.oathbound.event.GateRite;
import com.oathbound.event.GloamingTravel;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModTags;
import com.oathbound.util.Puzzles;
import com.oathbound.world.SketchPlacer;
import com.oathbound.world.Sketches;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.Vec3;

import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.Supplier;

/**
 * {@code /oathbound} — tools for server owners, modpack makers and content creators (op level 2): hand out
 * gear, raise any structure, wake any keeper, jump the story forward, open gates and cross to the Gloaming.
 */
public final class OathboundCommand {
    private static final Map<String, Supplier<? extends EntityType<? extends KeeperEntity>>> KEEPERS = Map.of(
        "caldris", ModEntities.SIR_CALDRIS, "veyl", ModEntities.ARCHMAGE_VEYL, "hrodgar", ModEntities.HRODGAR, "morvane", ModEntities.MORVANE);
    private static final Map<String, TagKey<Structure>> STRUCTURES = Map.of(
        "wayshrine", ModTags.WAYSHRINE, "drowned_chapel", ModTags.DROWNED_CHAPEL, "arcanist_spire", ModTags.ARCANIST_SPIRE,
        "barrow_of_kings", ModTags.BARROW, "sundered_citadel", ModTags.SUNDERED_CITADEL);

    private OathboundCommand() {}

    public static void register(CommandDispatcher<CommandSourceStack> d) {
        d.register(Commands.literal("oathbound")
            .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
            .executes(OathboundCommand::help)
            .then(Commands.literal("help").executes(OathboundCommand::help))
            .then(Commands.literal("kit").executes(OathboundCommand::kit))
            .then(Commands.literal("build").then(Commands.argument("sketch", StringArgumentType.word())
                .suggests((c, b) -> SharedSuggestionProvider.suggest(Arrays.stream(Sketches.Type.values()).map(Sketches.Type::id), b))
                .executes(OathboundCommand::build)))
            .then(Commands.literal("keeper").then(Commands.argument("name", StringArgumentType.word())
                .suggests((c, b) -> SharedSuggestionProvider.suggest(KEEPERS.keySet(), b))
                .executes(OathboundCommand::keeper)))
            .then(Commands.literal("stage").then(Commands.argument("quest", StringArgumentType.word())
                .suggests((c, b) -> SharedSuggestionProvider.suggest(QuestLog.QUESTS.keySet(), b))
                .executes(OathboundCommand::stage)))
            .then(Commands.literal("locate").then(Commands.argument("structure", StringArgumentType.word())
                .suggests((c, b) -> SharedSuggestionProvider.suggest(STRUCTURES.keySet(), b))
                .executes(OathboundCommand::locate)))
            .then(Commands.literal("gate").executes(OathboundCommand::gate))
            .then(Commands.literal("gloaming").executes(c -> {
                GloamingTravel.toGloaming(c.getSource().getPlayerOrException(), BlockPos.containing(c.getSource().getPosition()));
                return 1;
            }))
            .then(Commands.literal("home").executes(c -> {
                GloamingTravel.toOverworld(c.getSource().getPlayerOrException());
                return 1;
            })));
    }

    private static void say(CommandContext<CommandSourceStack> c, Component text) {
        c.getSource().sendSuccess(() -> text, false);
    }

    private static int help(CommandContext<CommandSourceStack> c) {
        for (String l : List.of("header", "kit", "build", "keeper", "stage", "locate", "gate", "gloaming", "home")) {
            say(c, Component.translatable("command.oathbound.help." + l).withStyle(l.equals("header") ? ChatFormatting.GOLD : ChatFormatting.GRAY));
        }
        return 1;
    }

    private static int kit(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        List<Supplier<? extends Item>> kit = List.of(ModItems.LANTERN_CHRONICLE, ModItems.WARDENS_LANTERN, ModItems.OATHSTEEL_LONGSWORD, ModItems.WARDENS_HALBERD,
            ModItems.DROWNED_ANCHOR, ModItems.STAFF_OF_VEYL, ModItems.DAWNSTRING_LONGBOW, ModItems.HOUSECARL_WARHORN, ModItems.SHADOWREAP_SICKLE,
            ModItems.DAWNBREAKER, ModItems.OATHKEY, ModItems.HOLLOW_CROWN, ModItems.OATHSTEEL_CHESTPLATE, ModItems.ARCANIST_ROBE);
        for (Supplier<? extends Item> s : kit) p.getInventory().add(new ItemStack(s.get()));
        p.getInventory().add(new ItemStack(ModItems.LUMEN_FLASK.get(), 16));
        p.getInventory().add(new ItemStack(ModItems.LUMENITE_SHARD.get(), 32));
        p.getInventory().add(new ItemStack(ModItems.ELIXIR_OF_DAWN.get(), 4));
        p.getInventory().add(new ItemStack(net.minecraft.world.item.Items.ARROW, 64));
        say(c, Component.translatable("command.oathbound.kit").withStyle(ChatFormatting.GOLD));
        return 1;
    }

    private static int build(CommandContext<CommandSourceStack> c) {
        Sketches.Type type;
        try {
            type = Sketches.Type.named(StringArgumentType.getString(c, "sketch"));
        } catch (IllegalArgumentException e) {
            c.getSource().sendFailure(Component.translatable("command.oathbound.unknown"));
            return 0;
        }
        ServerLevel level = c.getSource().getLevel();
        Vec3 pos = c.getSource().getPosition();
        Vec3 look = c.getSource().getEntity() != null ? c.getSource().getEntity().getLookAngle().multiply(1, 0, 1).normalize() : new Vec3(0, 0, 1);
        BlockPos at = BlockPos.containing(pos.add(look.scale(type.footprint + 6))).atY((int) Math.floor(pos.y) - 1);
        SketchPlacer.placeNow(level, Sketches.draw(type, level.getRandom().nextLong()), at);
        say(c, Component.translatable("command.oathbound.build", type.id(), at.getX(), at.getY(), at.getZ()).withStyle(ChatFormatting.GOLD));
        return 1;
    }

    private static int keeper(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        String name = StringArgumentType.getString(c, "name").toLowerCase(Locale.ROOT);
        var type = KEEPERS.get(name);
        if (type == null) {
            c.getSource().sendFailure(Component.translatable("command.oathbound.unknown"));
            return 0;
        }
        ServerLevel level = c.getSource().getLevel();
        ServerPlayer p = c.getSource().getPlayerOrException();
        KeeperEntity k = type.get().create(level, EntitySpawnReason.COMMAND);
        if (k == null) return 0;
        Vec3 at = p.position().add(p.getLookAngle().multiply(1, 0, 1).normalize().scale(10));
        k.snapTo(at.x, at.y, at.z, p.getYRot() + 180, 0);
        level.addFreshEntity(k);
        k.wake(level, p);
        say(c, Component.translatable("command.oathbound.keeper", k.getDisplayName()).withStyle(ChatFormatting.GOLD));
        return 1;
    }

    private static int stage(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        String target = StringArgumentType.getString(c, "quest");
        if (!QuestLog.QUESTS.containsKey(target)) {
            c.getSource().sendFailure(Component.translatable("command.oathbound.unknown"));
            return 0;
        }
        // grant the quest and its whole ancestry
        String q = target;
        int n = 0;
        while (q != null) {
            var holder = p.level().getServer().getAdvancements().get(QuestLog.questAdvancement(q));
            if (holder != null) {
                for (String criterion : holder.value().criteria().keySet()) p.getAdvancements().award(holder, criterion);
                n++;
            }
            q = QuestLog.QUESTS.get(q).parent();
        }
        QuestLog.syncAll(p);
        final int granted = n;
        say(c, Component.translatable("command.oathbound.stage", target, granted).withStyle(ChatFormatting.GOLD));
        return granted;
    }

    private static int locate(CommandContext<CommandSourceStack> c) {
        String name = StringArgumentType.getString(c, "structure");
        TagKey<Structure> tag = STRUCTURES.get(name);
        if (tag == null) {
            c.getSource().sendFailure(Component.translatable("command.oathbound.unknown"));
            return 0;
        }
        ServerLevel level = c.getSource().getLevel();
        BlockPos from = BlockPos.containing(c.getSource().getPosition());
        BlockPos found = level.findNearestMapStructure(tag, from, 100, false);
        if (found == null) {
            c.getSource().sendFailure(Component.translatable("command.oathbound.locate.none"));
            return 0;
        }
        int dist = (int) Math.sqrt(found.distSqr(from.atY(found.getY())));
        say(c, Component.translatable("command.oathbound.locate", name, found.getX(), found.getZ(), dist).withStyle(ChatFormatting.GOLD));
        return 1;
    }

    private static int gate(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        List<BlockPos> keys = Puzzles.find(level, BlockPos.containing(c.getSource().getPosition()), 24, ModBlocks.SUNDERED_KEYSTONE.get());
        if (keys.isEmpty()) {
            c.getSource().sendFailure(Component.translatable("command.oathbound.gate.none"));
            return 0;
        }
        int n = GateRite.openNow(level, keys.get(0));
        say(c, Component.translatable("command.oathbound.gate", n).withStyle(ChatFormatting.GOLD));
        return 1;
    }
}
