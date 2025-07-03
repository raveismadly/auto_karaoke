
package com.raveismadly;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

public class AutoKaraokeApp extends Application {

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("Auto Karaoke");

        VBox root = new VBox();
        Scene scene = new Scene(root, 1024, 768);

        // Add styling or layout configurations here
        // scene.getStylesheets().add(getClass().getResource("/main.css").toExternalForm());

        Button btn = new Button("Add Song");

        // Placeholder for adding song functionality
        btn.setOnAction(event -> {
            // Logic to select audio file and generate karaoke will be implemented here
        });

        root.getChildren().add(btn);
        primaryStage.setScene(scene);
        primaryStage.show();
    }
}
