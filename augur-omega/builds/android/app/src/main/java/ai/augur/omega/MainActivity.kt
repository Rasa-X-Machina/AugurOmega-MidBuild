package ai.augur.omega

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.TextView
import android.util.Log

class MainActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "AugurOmega"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val textView = TextView(this)
        textView.text = "Augur Omega AI Platform Running!"
        setContentView(textView)
        
        Log.d(TAG, "Augur Omega Android App Started")
    }
}
