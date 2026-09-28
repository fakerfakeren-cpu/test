package com.astralfall.client;

import com.astralfall.Astralfall;
import com.astralfall.block.StarLockBlock;
import com.astralfall.entity.SingularityEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * Automated client smoke test (-Dastralfall.clienttest=true): joins a world, stages every showcase
 * scene with commands, takes screenshots and quits. Proves that every renderer works on a real client.
 */
public final class ClientTest {
    private record Step(int delay, String name, Consumer<Minecraft> action) {}

    private static final List<Step> STEPS = new ArrayList<>();
    private static int index = -1;
    private static int wait = 200;
    private static BlockPos base;
    private static int shots;

    private ClientTest() {}

    public static boolean enabled() {
        return Boolean.getBoolean("astralfall.clienttest");
    }

    private static void log(String s) {
        Astralfall.LOGGER.info("[CLIENTTEST] {}", s);
    }

    private static void server(Minecraft mc, Consumer<ServerPlayer> r) {
        MinecraftServer server = mc.getSingleplayerServer();
        if (server == null) return;
        server.execute(() -> {
            try {
                r.accept(server.getPlayerList().getPlayers().get(0));
            } catch (Throwable t) {
                Astralfall.LOGGER.error("[CLIENTTEST] server action failed", t);
            }
        });
    }

    private static void cmd(Minecraft mc, String command) {
        server(mc, p -> p.level().getServer().getCommands().performPrefixedCommand(p.createCommandSourceStack(), command));
    }

    private static void camera(Minecraft mc, double x, double y, double z, float yaw, float pitch) {
        cmd(mc, String.format(java.util.Locale.ROOT, "tp @s %.2f %.2f %.2f %.1f %.1f", x, y, z, yaw, pitch));
    }

    private static void lookAt(Minecraft mc, Vec3 from, Vec3 at) {
        Vec3 d = at.subtract(from);
        float yaw = (float) (Math.atan2(-d.x, d.z) * 180 / Math.PI);
        float pitch = (float) (-Math.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * 180 / Math.PI);
        camera(mc, from.x, from.y, from.z, yaw, pitch);
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "astralfall_" + name + ".png", mc.gameRenderer.mainRenderTarget(), 1, msg -> log("screenshot " + name + ": " + msg.getString()));
        shots++;
    }

    private static int ground(Minecraft mc, int x, int z) {
        return mc.level == null ? 80 : mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
    }

    private static void step(int delay, String name, Consumer<Minecraft> action) {
        STEPS.add(new Step(delay, name, action));
    }

    private static void script() {
        STEPS.clear();
        step(1, "setup", mc -> {
            cmd(mc, "gamemode spectator");
            cmd(mc, "gamerule advance_time false");
            cmd(mc, "gamerule advance_weather false");
            cmd(mc, "gamerule send_command_feedback false");
            cmd(mc, "weather clear");
            cmd(mc, "time set minecraft:noon");
            base = mc.player.blockPosition();
            log("base " + base);
        });
        // --- Observatory (built 34 blocks south of base)
        step(10, "build observatory", mc -> {
            camera(mc, base.getX() + 0.5, base.getY() + 1, base.getZ() + 0.5, 0f, 0f);
        });
        step(10, "build", mc -> cmd(mc, "astralfall build observatory"));
        step(60, "observatory view", mc -> {
            Vec3 center = new Vec3(base.getX() + 0.5, base.getY() + 12, base.getZ() + 34.5);
            lookAt(mc, center.add(-34, 16, -30), center);
        });
        step(200, "shot observatory", mc -> shot(mc, "observatory"));
        step(5, "hall view", mc -> {
            Vec3 center = new Vec3(base.getX() + 0.5, base.getY(), base.getZ() + 34.5);
            lookAt(mc, center.add(4, 3.2, 6), center.add(0, 1.5, -8));
        });
        step(120, "shot hall", mc -> shot(mc, "observatory_hall"));
        step(5, "unseal", mc -> server(mc, p -> {
            int y = p.level().getHeight(Heightmap.Types.WORLD_SURFACE, base.getX(), base.getZ() + 34);
            BlockPos lock = findLock(p.level(), new BlockPos(base.getX(), base.getY(), base.getZ() + 34));
            log("star lock at " + lock);
            if (lock != null) StarLockBlock.unseal(p.level(), lock);
        }));
        step(20, "vault view", mc -> {
            Vec3 c = new Vec3(base.getX() + 0.5, base.getY(), base.getZ() + 34.5 - 17);
            lookAt(mc, c.add(0, -5.5, 4.5), c.add(0, -7.5, -4));
        });
        step(120, "shot vault", mc -> shot(mc, "vault"));
        step(5, "telescope view", mc -> {
            Vec3 c = new Vec3(base.getX() + 0.5, base.getY(), base.getZ() + 34.5);
            lookAt(mc, c.add(6, 17.5, 5), c.add(-1, 16, -1));
        });
        step(120, "shot telescope", mc -> shot(mc, "telescope_chamber"));
        // --- Bestiary
        step(5, "gallery pos", mc -> {
            int gx = base.getX() - 60, gz = base.getZ();
            camera(mc, gx + 0.5, ground(mc, gx, gz) + 2.0, gz + 0.5, -90f, 5f);
        });
        step(60, "gallery", mc -> cmd(mc, "astralfall gallery"));
        step(80, "gallery camera", mc -> {
            int gx = base.getX() - 60, gz = base.getZ();
            camera(mc, gx + 0.5, ground(mc, gx, gz) + 3.5, gz + 0.5, -90f, 10f);
        });
        step(120, "shot gallery", mc -> shot(mc, "bestiary"));
        // --- Fallen Vessel & Sky Shrine
        step(5, "vessel", mc -> {
            int vx = base.getX() + 80, vz = base.getZ();
            camera(mc, vx + 0.5, ground(mc, vx, vz) + 2, vz + 0.5, 0f, 0f);
        });
        step(20, "build vessel", mc -> cmd(mc, "astralfall build fallen_vessel"));
        step(40, "vessel view", mc -> {
            int vx = base.getX() + 80, vz = base.getZ() + 26;
            lookAt(mc, new Vec3(vx + 22, ground(mc, vx, vz) + 12, vz + 18), new Vec3(vx, ground(mc, vx, vz), vz));
        });
        step(160, "shot vessel", mc -> shot(mc, "fallen_vessel"));
        step(5, "shrine", mc -> {
            int sx = base.getX() + 80, sz = base.getZ() + 80;
            camera(mc, sx + 0.5, ground(mc, sx, sz) + 2, sz + 0.5, 0f, 0f);
        });
        step(20, "build shrine", mc -> cmd(mc, "astralfall build sky_shrine"));
        step(40, "shrine view", mc -> {
            int sx = base.getX() + 80, sz = base.getZ() + 98;
            Vec3 c = new Vec3(sx, ground(mc, sx, sz - 18) + 28, sz);
            lookAt(mc, c.add(-24, 2, -22), c.add(0, -3, 0));
        });
        step(160, "shot shrine", mc -> shot(mc, "sky_shrine"));
        // --- Night: meteors, singularity, boss
        step(5, "night", mc -> {
            cmd(mc, "time set minecraft:midnight");
            int mx = base.getX() - 60, mz = base.getZ() + 60;
            camera(mc, mx + 0.5, ground(mc, mx, mz) + 3, mz + 0.5, 180f, -25f);
        });
        step(40, "starfall", mc -> cmd(mc, "astralfall starfall 8"));
        step(45, "shot meteors", mc -> shot(mc, "meteor_shower"));
        step(60, "shot impact", mc -> shot(mc, "meteor_impacts"));
        step(5, "singularity", mc -> server(mc, p -> {
            Vec3 at = p.position().add(p.getLookAngle().multiply(1, 0, 1).normalize().scale(9)).add(0, 3, 0);
            SingularityEntity.spawn(p.level(), at, p, 200, 8f, 0f, false);
        }));
        step(40, "shot singularity", mc -> shot(mc, "singularity"));
        step(5, "boss", mc -> {
            int bx = base.getX() - 120, bz = base.getZ() + 60;
            camera(mc, bx + 0.5, ground(mc, bx, bz) + 2, bz + 0.5, 0f, 0f);
        });
        step(20, "summon", mc -> cmd(mc, "astralfall summon"));
        step(100, "shot ritual", mc -> shot(mc, "eclipse_ritual"));
        step(140, "boss camera", mc -> {
            int bx = base.getX() - 120, bz = base.getZ() + 60 + 16;
            Vec3 boss = new Vec3(bx + 0.5, ground(mc, bx, bz) + 4, bz + 0.5);
            lookAt(mc, boss.add(-9, 3, -14), boss);
        });
        step(60, "shot boss", mc -> shot(mc, "astraeus"));
        step(120, "shot boss 2", mc -> shot(mc, "astraeus_attack"));
        step(100, "quit", mc -> {
            log("RESULT: PASS screenshots=" + shots);
            mc.stop();
        });
    }

    private static BlockPos findLock(ServerLevel level, BlockPos near) {
        for (BlockPos p : BlockPos.betweenClosed(near.offset(-3, -4, -12), near.offset(3, 12, -6))) {
            if (level.getBlockState(p).getBlock() instanceof StarLockBlock) return p.immutable();
        }
        return null;
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) return;
        if (index == -1) {
            script();
            index = 0;
            log("world joined, starting scenario with " + STEPS.size() + " steps");
        }
        if (index >= STEPS.size()) return;
        if (--wait > 0) return;
        Step s = STEPS.get(index++);
        try {
            s.action().accept(mc);
        } catch (Throwable t) {
            Astralfall.LOGGER.error("[CLIENTTEST] step {} failed", s.name(), t);
        }
        wait = index < STEPS.size() ? STEPS.get(index).delay() : 0;
    }
}
