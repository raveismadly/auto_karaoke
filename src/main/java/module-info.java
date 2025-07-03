
module com.raveismadly.autokaraoke {
    requires javafx.controls;
    requires javafx.base;
    requires transitive javafx.graphics;

    exports com.raveismadly;
    opens com.raveismadly; // For FXML loading
}
