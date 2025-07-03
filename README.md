Initial commit on main branch


# Auto Karaoke

Auto Karaoke is an application to automatically generate karaoke files from music tracks.

## Prerequisites
- **Java Development Kit (JDK)**: Ensure you have JDK 17 installed on your system.
- **Maven**: Make sure you have Maven installed.

## Setup Instructions

1. **Clone the repository**:
    ```
    git clone https://github.com/raveismadly/auto_karaoke.git
    ```

2. **Navigate to the project directory**:
    ```
    cd auto_karaoke
    ```

3. **Compile and package the project using Maven** (this step may require administrator privileges on Windows):
    ```
    mvn clean package
    ```

4. **Finding the generated files**:
    - The `.app` or `.dmg` file will be located in `./target/app/`

5. **Opening the generated file**
    - For `.app` files (macOS), navigate to `target/app`, select the generated `.app` file, and double-click it to run the application.
    - For other formats like `.exe`, the files are also in the same location.

## Troubleshooting:

### Problem: Build fails with package errors
#### Common Fixes:
1. Make sure that you have run:
    ```
    apt-get update && apt-get install -y maven openjdk-11-jdk-headless
    ```
2. Run the following commands:
    ```
    mvn clean
    mvn install
    mvn package
    ```
3. Delete the `~/.m2/repository` directory or remove the existing `maven-metadata-*.jar` files.

#### Platform-Specific Troubleshooting:
**Windows**:
- Sometimes, the app might not compile correctly due to missing libraries. Try running the command as an administrator.
- Ensure `JAVA_HOME` environment variable is correctly set to your JDK location.

**MacOS**:
- When creating a build on MacOS, you may want to specify the type as `dmg` in the `pom.xml`.
- Run `mvn -U clean package -P package-mac` to re-run the packaging phase for MacOS.

Update on develop branch
Feature branch update

