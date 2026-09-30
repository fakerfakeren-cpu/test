package com.oathbound;

import net.minecraftforge.common.ForgeConfigSpec;

/** Server/common tunables. Values are read lazily so they are safe to query at any time. */
public final class Config {
    private static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();

    public static final ForgeConfigSpec.BooleanValue GIVE_CHRONICLE = BUILDER
        .comment("Give every player the Lantern Chronicle the first time they join a world.")
        .define("giveChronicleOnFirstJoin", true);
    public static final ForgeConfigSpec.DoubleValue KEEPER_HEALTH_MULTIPLIER = BUILDER
        .comment("Health multiplier for the seal keepers (Caldris, Veyl, Hrodgar) and the wild keepers (Elderhorn, Bog Mother, Cinder Colossus).")
        .defineInRange("keeperHealthMultiplier", 1.0, 0.1, 20.0);
    public static final ForgeConfigSpec.DoubleValue BOSS_HEALTH_MULTIPLIER = BUILDER
        .comment("Health multiplier for Morvane, the Hollow King (useful for multiplayer servers).")
        .defineInRange("bossHealthMultiplier", 1.0, 0.1, 20.0);
    public static final ForgeConfigSpec.BooleanValue GLOAMROT = BUILDER
        .comment("The Gloaming inflicts Gloamrot on players who carry no lit lantern.")
        .define("gloamrot", true);
    public static final ForgeConfigSpec.BooleanValue LANTERN_LIGHT = BUILDER
        .comment("A Warden's Lantern held in either hand lights up the area around its bearer.")
        .define("lanternLight", true);
    public static final ForgeConfigSpec.BooleanValue SKIP_EXPERIMENTAL_WARNING = BUILDER
        .comment("Client: skip vanilla's 'Experimental Settings' prompts, which appear for any mod that adds world",
                 "generation or dimensions through data packs. Equivalent to clicking 'I Know What I'm Doing!'.")
        .define("skipExperimentalWarning", true);
    public static final ForgeConfigSpec.BooleanValue AMBIENT_LIFE = BUILDER
        .comment("Client: the world's ambience. Fireflies, blossoms, glowing plankton, spores, ash and cave motes around you,",
                 "and birdsong, crickets, owls, frogs and wind. Follows the video settings' particle level.")
        .define("ambientLife", true);

    public static final ForgeConfigSpec SPEC = BUILDER.build();

    private Config() {}

    public static boolean giveChronicle() { return safe(() -> GIVE_CHRONICLE.get(), true); }
    public static double keeperHealthMultiplier() { return safe(() -> KEEPER_HEALTH_MULTIPLIER.get(), 1.0); }
    public static double bossHealthMultiplier() { return safe(() -> BOSS_HEALTH_MULTIPLIER.get(), 1.0); }
    public static boolean gloamrot() { return safe(() -> GLOAMROT.get(), true); }
    public static boolean lanternLight() { return safe(() -> LANTERN_LIGHT.get(), true); }
    public static boolean skipExperimentalWarning() { return safe(() -> SKIP_EXPERIMENTAL_WARNING.get(), true); }
    public static boolean ambientLife() { return safe(() -> AMBIENT_LIFE.get(), true); }

    private static <T> T safe(java.util.function.Supplier<T> s, T fallback) {
        try {
            return s.get();
        } catch (Throwable t) {
            return fallback;
        }
    }
}
