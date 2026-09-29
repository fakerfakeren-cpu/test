package com.rimeheart.command;

import com.rimeheart.entity.boss.SovereignRitual;
import com.rimeheart.registry.ModItems;
import com.rimeheart.registry.ModTags;
import com.rimeheart.world.BlueprintPlacer;
import com.rimeheart.world.Blueprints;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

import java.util.List;
import java.util.function.Supplier;

/** {@code /rimeheart} admin and showcase commands (permission level 2). */
public final class RimeheartCommand {
    private RimeheartCommand() {}

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("rimeheart")
            .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
            .executes(RimeheartCommand::help)
            .then(Commands.literal("help").executes(RimeheartCommand::help))
            .then(Commands.literal("kit").executes(RimeheartCommand::kit))
            .then(Commands.literal("summon").executes(RimeheartCommand::summon))
            .then(Commands.literal("build").then(Commands.literal("sanctum").executes(RimeheartCommand::build)))
            .then(Commands.literal("locate").then(Commands.literal("sanctum").executes(RimeheartCommand::locate))));
    }

    private static int help(CommandContext<CommandSourceStack> c) {
        for (String l : new String[]{"header", "kit", "summon", "build", "locate"}) {
            c.getSource().sendSuccess(() -> Component.translatable("command.rimeheart.help." + l).withStyle(l.equals("header") ? ChatFormatting.AQUA : ChatFormatting.GRAY), false);
        }
        return 1;
    }

    private static int kit(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        List<Supplier<? extends Item>> items = List.of(
            ModItems.WARDENS_JOURNAL, ModItems.FROSTBITE_BLADE, ModItems.GLACIER_MAUL, ModItems.RIMEBOW, ModItems.BLIZZARD_STAFF, ModItems.WINTERFANG,
            ModItems.FROSTIRON_PICKAXE, ModItems.WINTER_HORN, ModItems.HEARTHFIRE_STEW,
            ModItems.FROSTIRON_HELMET, ModItems.FROSTIRON_CHESTPLATE, ModItems.FROSTIRON_LEGGINGS, ModItems.FROSTIRON_BOOTS,
            ModItems.WRAITHWEAVE_HOOD, ModItems.WRAITHWEAVE_ROBE, ModItems.WRAITHWEAVE_LEGGINGS, ModItems.WRAITHWEAVE_BOOTS);
        for (var s : items) give(p, new ItemStack(s.get()));
        give(p, new ItemStack(ModItems.FROST_CHARGE.get(), 16));
        give(p, new ItemStack(ModItems.RIME_SHARD.get(), 16));
        c.getSource().sendSuccess(() -> Component.translatable("command.rimeheart.kit").withStyle(ChatFormatting.AQUA), false);
        return 1;
    }

    private static void give(ServerPlayer p, ItemStack stack) {
        if (!p.getInventory().add(stack)) p.drop(stack, false);
    }

    private static int summon(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        Vec3 pos = c.getSource().getPosition();
        Vec3 look = c.getSource().getEntity() != null ? c.getSource().getEntity().getLookAngle() : new Vec3(1, 0, 0);
        BlockPos at = BlockPos.containing(pos.add(new Vec3(look.x, 0, look.z).normalize().scale(10)));
        SovereignRitual.begin(level, at);
        return 1;
    }

    private static int build(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        BlockPos at = BlockPos.containing(c.getSource().getPosition()).below();
        BlueprintPlacer.placeNow(level, Blueprints.build(Blueprints.Type.FROZEN_SANCTUM, level.getRandom().nextLong()), at);
        c.getSource().sendSuccess(() -> Component.translatable("command.rimeheart.build").withStyle(ChatFormatting.AQUA), true);
        return 1;
    }

    private static int locate(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        BlockPos from = BlockPos.containing(c.getSource().getPosition());
        BlockPos found = level.findNearestMapStructure(ModTags.FROZEN_SANCTUM, from, 100, false);
        if (found == null) {
            c.getSource().sendFailure(Component.translatable("command.rimeheart.locate.none"));
            return 0;
        }
        int dist = (int) Math.sqrt(from.distSqr(new BlockPos(found.getX(), from.getY(), found.getZ())));
        c.getSource().sendSuccess(() -> Component.translatable("command.rimeheart.locate", found.getX(), found.getZ(), dist).withStyle(ChatFormatting.AQUA), false);
        return 1;
    }
}
