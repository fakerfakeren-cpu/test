package com.astralfall.command;

import com.astralfall.entity.boss.BossSummoner;
import com.astralfall.event.Starfall;
import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModItems;
import com.astralfall.registry.ModTags;
import com.astralfall.world.Blueprints;
import com.astralfall.world.BlueprintPlacer;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

import java.util.List;
import java.util.function.Supplier;

/**
 * /astralfall — showcase and testing commands.
 * <pre>
 *   help | kit | starfall [count] | fallenstar | starstorm [stop] | summon
 *   build (observatory|fallen_vessel|sky_shrine|crater) | locate (observatory|fallen_vessel|sky_shrine) | gallery
 * </pre>
 */
public final class AstralfallCommand {
    private AstralfallCommand() {}

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("astralfall")
            .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
            .executes(AstralfallCommand::help)
            .then(Commands.literal("help").executes(AstralfallCommand::help))
            .then(Commands.literal("kit").executes(AstralfallCommand::kit))
            .then(Commands.literal("starfall")
                .executes(c -> starfall(c, 5))
                .then(Commands.argument("count", IntegerArgumentType.integer(1, 50)).executes(c -> starfall(c, IntegerArgumentType.getInteger(c, "count")))))
            .then(Commands.literal("fallenstar").executes(AstralfallCommand::fallenStar))
            .then(Commands.literal("starstorm")
                .executes(AstralfallCommand::starstorm)
                .then(Commands.literal("stop").executes(c -> {
                    Starfall.endStarstorm(c.getSource().getLevel());
                    return 1;
                })))
            .then(Commands.literal("summon").executes(AstralfallCommand::summon))
            .then(Commands.literal("gallery").executes(AstralfallCommand::gallery))
            .then(Commands.literal("build")
                .then(Commands.argument("structure", StringArgumentType.word())
                    .suggests((c, b) -> SharedSuggestionProvider.suggest(List.of("observatory", "fallen_vessel", "sky_shrine", "crater"), b))
                    .executes(AstralfallCommand::build)))
            .then(Commands.literal("locate")
                .then(Commands.argument("structure", StringArgumentType.word())
                    .suggests((c, b) -> SharedSuggestionProvider.suggest(List.of("observatory", "fallen_vessel", "sky_shrine"), b))
                    .executes(AstralfallCommand::locate))));
    }

    private static int help(CommandContext<CommandSourceStack> c) {
        CommandSourceStack src = c.getSource();
        String[] lines = {"header", "kit", "starfall", "fallenstar", "starstorm", "summon", "build", "locate", "gallery"};
        for (String l : lines) {
            src.sendSuccess(() -> Component.translatable("command.astralfall.help." + l).withStyle(l.equals("header") ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.GRAY), false);
        }
        return 1;
    }

    private static int kit(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        List<Supplier<? extends net.minecraft.world.item.Item>> items = List.of(
            ModItems.ASTRAL_JOURNAL, ModItems.STARBLADE, ModItems.COMET_MAUL, ModItems.RIFTCALLER, ModItems.CONSTELLATION_BOW,
            ModItems.ECLIPSE_GREATSWORD, ModItems.GRAVITY_GAUNTLET, ModItems.ASTRAL_COMPASS, ModItems.STARMETAL_PICKAXE,
            ModItems.ECLIPSE_SIGIL, ModItems.CROWN_OF_ASTRAEUS, ModItems.NEBULA_WINGS,
            ModItems.STARMETAL_HELMET, ModItems.STARMETAL_CHESTPLATE, ModItems.STARMETAL_LEGGINGS, ModItems.STARMETAL_BOOTS,
            ModItems.VOIDWALKER_HELMET, ModItems.VOIDWALKER_CHESTPLATE, ModItems.VOIDWALKER_LEGGINGS, ModItems.VOIDWALKER_BOOTS);
        for (var s : items) give(p, new ItemStack(s.get()));
        give(p, new ItemStack(ModItems.SINGULARITY_GRENADE.get(), 16));
        give(p, new ItemStack(ModItems.STARDUST.get(), 16));
        give(p, new ItemStack(ModItems.SKYSHARD.get(), 16));
        c.getSource().sendSuccess(() -> Component.translatable("command.astralfall.kit").withStyle(ChatFormatting.AQUA), false);
        return 1;
    }

    private static void give(ServerPlayer p, ItemStack stack) {
        if (!p.getInventory().add(stack)) p.drop(stack, false);
    }

    private static int starfall(CommandContext<CommandSourceStack> c, int count) {
        ServerLevel level = c.getSource().getLevel();
        Vec3 pos = c.getSource().getPosition();
        var rand = level.getRandom();
        for (int i = 0; i < count; i++) {
            double a = rand.nextDouble() * Math.PI * 2, d = 16 + rand.nextDouble() * 40;
            BlockPos target = BlockPos.containing(pos.x + Math.cos(a) * d, pos.y, pos.z + Math.sin(a) * d);
            int roll = rand.nextInt(10);
            Starfall.Variant v = roll == 0 ? Starfall.Variant.FALLEN_STAR : roll < 3 ? Starfall.Variant.CRAWLER : Starfall.Variant.NORMAL;
            Starfall.spawnMeteor(level, target, v, 1.3f + rand.nextFloat() * 1.2f);
        }
        c.getSource().sendSuccess(() -> Component.translatable("command.astralfall.starfall", count).withStyle(ChatFormatting.GOLD), true);
        return count;
    }

    private static int fallenStar(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        Vec3 pos = c.getSource().getPosition();
        Vec3 look = c.getSource().getEntity() != null ? c.getSource().getEntity().getLookAngle() : new Vec3(1, 0, 0);
        BlockPos target = BlockPos.containing(pos.add(new Vec3(look.x, 0, look.z).normalize().scale(20)));
        Starfall.spawnMeteor(level, target, Starfall.Variant.FALLEN_STAR, 2.0f);
        c.getSource().sendSuccess(() -> Component.translatable("command.astralfall.fallenstar").withStyle(ChatFormatting.GOLD), true);
        return 1;
    }

    private static int starstorm(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        if (!level.isDarkOutside()) {
            level.getServer().getCommands().performPrefixedCommand(level.getServer().createCommandSourceStack().withSuppressedOutput(), "time set minecraft:night");
        }
        Starfall.startStarstorm(level, 20 * 90);
        return 1;
    }

    private static int summon(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        Vec3 pos = c.getSource().getPosition();
        Vec3 look = c.getSource().getEntity() != null ? c.getSource().getEntity().getLookAngle() : new Vec3(1, 0, 0);
        BlockPos at = BlockPos.containing(pos.add(new Vec3(look.x, 0, look.z).normalize().scale(16)));
        at = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at);
        if (BossSummoner.isRitualActive(level)) {
            c.getSource().sendFailure(Component.translatable("message.astralfall.altar.busy"));
            return 0;
        }
        BossSummoner.begin(level, at);
        return 1;
    }

    private static int build(CommandContext<CommandSourceStack> c) {
        String name = StringArgumentType.getString(c, "structure");
        Blueprints.Type type;
        try {
            type = Blueprints.Type.byName(name);
        } catch (IllegalArgumentException e) {
            c.getSource().sendFailure(Component.literal("Unknown structure: " + name));
            return 0;
        }
        ServerLevel level = c.getSource().getLevel();
        Vec3 pos = c.getSource().getPosition();
        Vec3 look = c.getSource().getEntity() != null ? c.getSource().getEntity().getLookAngle() : new Vec3(1, 0, 0);
        double dist = switch (type) {
            case OBSERVATORY -> 34;
            case FALLEN_VESSEL -> 26;
            case SKY_SHRINE -> 18;
            case CRATER -> 12;
        };
        BlockPos center = BlockPos.containing(pos.add(new Vec3(look.x, 0, look.z).normalize().scale(dist)));
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, center.getX(), center.getZ());
        int yOff = switch (type) {
            case FALLEN_VESSEL -> -2;
            case SKY_SHRINE -> 28;
            case CRATER -> 0;
            default -> 0;
        };
        BlockPos origin = new BlockPos(center.getX(), y + yOff, center.getZ());
        BlueprintPlacer.placeNow(level, Blueprints.build(type, level.getRandom().nextLong()), origin);
        c.getSource().sendSuccess(() -> Component.translatable("command.astralfall.build", Component.translatable("structure.astralfall." + type.id()), origin.getX(), origin.getY(), origin.getZ()).withStyle(ChatFormatting.AQUA), true);
        return 1;
    }

    private static int locate(CommandContext<CommandSourceStack> c) {
        String name = StringArgumentType.getString(c, "structure");
        var tag = switch (name) {
            case "fallen_vessel" -> ModTags.FALLEN_VESSEL;
            case "sky_shrine" -> ModTags.SKY_SHRINE;
            default -> ModTags.OBSERVATORY;
        };
        ServerLevel level = c.getSource().getLevel();
        BlockPos from = BlockPos.containing(c.getSource().getPosition());
        BlockPos found = level.findNearestMapStructure(tag, from, 100, false);
        if (found == null) {
            c.getSource().sendFailure(Component.translatable("message.astralfall.compass.none", Component.translatable("structure.astralfall." + name)));
            return 0;
        }
        int dist = (int) Math.sqrt(from.distSqr(new BlockPos(found.getX(), from.getY(), found.getZ())));
        c.getSource().sendSuccess(() -> Component.translatable("command.astralfall.locate", Component.translatable("structure.astralfall." + name), found.getX(), found.getZ(), dist).withStyle(ChatFormatting.AQUA), false);
        return 1;
    }

    /** Spawns one of every creature in a row, frozen in place, for filming. */
    private static int gallery(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        Vec3 pos = c.getSource().getPosition();
        Vec3 look = c.getSource().getEntity() != null ? c.getSource().getEntity().getLookAngle() : new Vec3(1, 0, 0);
        Vec3 fwd = new Vec3(look.x, 0, look.z).normalize();
        Vec3 right = fwd.cross(new Vec3(0, 1, 0)).normalize();
        List<Supplier<? extends EntityType<? extends Mob>>> types = List.of(ModEntities.ASTRAL_WISP, ModEntities.VOID_STALKER, ModEntities.METEORITE_CRAWLER, ModEntities.VOID_GAZER, ModEntities.ASTRAEUS);
        double[] offsets = {-9, -4.5, 0, 4.5, 11};
        for (int i = 0; i < types.size(); i++) {
            Mob m = types.get(i).get().create(level, EntitySpawnReason.COMMAND);
            if (m == null) continue;
            Vec3 at = pos.add(fwd.scale(i == 4 ? 16 : 8)).add(right.scale(offsets[i]));
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, (int) Math.floor(at.x), (int) Math.floor(at.z));
            float yaw = (float) (Math.atan2(-fwd.z, -fwd.x) * 180 / Math.PI) - 90f;
            m.snapTo(at.x, y + (m instanceof com.astralfall.entity.mob.AstralWispEntity || m instanceof com.astralfall.entity.mob.VoidGazerEntity ? 1.5 : 0), at.z, yaw, 0);
            m.setYHeadRot(yaw);
            m.setYBodyRot(yaw);
            m.setNoAi(true);
            m.setPersistenceRequired();
            m.setCustomName(Component.translatable(m.getType().getDescriptionId()));
            m.setCustomNameVisible(true);
            level.addFreshEntity(m);
        }
        c.getSource().sendSuccess(() -> Component.translatable("command.astralfall.gallery").withStyle(ChatFormatting.AQUA), false);
        return 1;
    }
}
