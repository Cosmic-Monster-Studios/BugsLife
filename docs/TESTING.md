# Regression tests

Use JDK 21 and the project's pinned NeoForge/ModDevGradle versions. `./gradlew check` compiles and runs the native dedicated GameTest regression suite. `./gradlew runGameTestServer` runs it separately. These tests do not need a GPU or a client window.

Test classes and the empty structure are in `src/gametest/`, a separate source set loaded only by the GameTest server. They are not packaged in the release jar or loaded by ordinary development clients/servers. The suite exercises creative harvest overflow and partial merging, full-inventory capture conservation, collider-safe net assistance, grounded attachment with falling velocity, adjacent ceiling-bound breeding and offspring growth without embedding, cancellation after ceiling removal, a pending web after a policy flip, and two pending web writers racing for the local cap.

The default GameTest working directory and JUnit XML report are outside the repository at `<java.io.tmpdir>/bugslife-native-regressions/`. For isolated CI runs, pass an absolute external directory:

```powershell
.\gradlew.bat check -Pbugslife.test_run_dir=C:/external/bugslife-regressions
```

A stale report is removed before launch. Successful server exit alone is insufficient: the task requires all nine test cases in a fresh `junit.xml`, without skipped, failed, or errored cases. GameTest servers tick without normal real-time pacing; this suite makes no performance/TPS claim. Avoid concurrent runs sharing the same test directory.

Recipe-book discovery also has standalone product generator tests:

```powershell
python -B -m unittest discover -s tools/tests -p test_recipe_unlocks.py -v
```

They check every shipped recipe receives discovery, generation preserves all crafting inputs and unrelated advancements, component ingredients use a base-item discovery predicate without relaxing the crafting ingredient, and unsupported selectors fail. Generated test assets stay in temporary directories.

The source-set configuration follows the official [ModDevGradle isolated-source and run configuration APIs](https://github.com/neoforged/ModDevGradle#isolated-source-sets), and registration uses NeoForge's [1.21.1 GameTest API](https://docs.neoforged.net/docs/1.21.1/misc/gametest/).
