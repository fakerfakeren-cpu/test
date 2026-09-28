package com.astralfall;

import net.minecraftforge.common.ForgeConfigSpec;

/** Server/common tunables. Values are read lazily so they are safe to query at any time. */
public final class Config {
    private static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();

    public static final ForgeConfigSpec.BooleanValue METEOR_SHOWERS = BUILDER
        .comment("Meteors fall near players at night.")
        .define("meteorShowers", true);
    public static final ForgeConfigSpec.IntValue METEOR_CHANCE = BUILDER
        .comment("On a normal night, each player has a 1 in N chance per tick of a meteor impact nearby (lower = more meteors).")
        .defineInRange("meteorChance", 2400, 50, 1_000_000);
    public static final ForgeConfigSpec.IntValue STARSTORM_CHANCE = BUILDER
        .comment("1 in N nights becomes a Starstorm with far more meteors. 0 disables natural starstorms.")
        .defineInRange("starstormChance", 7, 0, 1000);
    public static final ForgeConfigSpec.BooleanValue METEOR_CRATERS = BUILDER
        .comment("Meteor impacts carve craters into the terrain (never touches blocks with block entities).")
        .define("meteorCraters", true);
    public static final ForgeConfigSpec.DoubleValue BOSS_HEALTH_MULTIPLIER = BUILDER
        .comment("Multiplier for Astraeus' health.")
        .defineInRange("bossHealthMultiplier", 1.0, 0.1, 20.0);
    public static final ForgeConfigSpec.BooleanValue SKIP_EXPERIMENTAL_WARNING = BUILDER
        .comment("Client: skip vanilla's 'Experimental Settings' prompts, which appear for any mod that adds world",
                 "generation through data packs. Equivalent to clicking 'I Know What I'm Doing!' (no backup is made).")
        .define("skipExperimentalWarning", true);

    public static final ForgeConfigSpec SPEC = BUILDER.build();

    private Config() {}

    public static boolean meteorShowers() { return safe(() -> METEOR_SHOWERS.get(), true); }
    public static int meteorChance() { return safe(() -> METEOR_CHANCE.get(), 2400); }
    public static int starstormChance() { return safe(() -> STARSTORM_CHANCE.get(), 7); }
    public static boolean meteorCraters() { return safe(() -> METEOR_CRATERS.get(), true); }
    public static double bossHealthMultiplier() { return safe(() -> BOSS_HEALTH_MULTIPLIER.get(), 1.0); }
    public static boolean skipExperimentalWarning() { return safe(() -> SKIP_EXPERIMENTAL_WARNING.get(), true); }

    private static <T> T safe(java.util.function.Supplier<T> s, T fallback) {
        try {
            return s.get();
        } catch (Throwable t) {
            return fallback;
        }
    }
}
