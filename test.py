package com.example.batt

import android.Manifest
import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import kotlinx.coroutines.*
import java.io.IOException
import java.util.*

class MainActivity : AppCompatActivity() {

    private val REQUEST_ENABLE_BT = 1
    private val REQUEST_LOCATION_PERMISSIONS = 2
    private val DEVICE_ADDRESS = "B8:27:EB:43:A9:DD" // 실제 블루투스 장치의 주소로 변경
    private val UUID_INSECURE = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    private var bluetoothAdapter: BluetoothAdapter? = null
    private var bluetoothSocket: BluetoothSocket? = null
    private var isConnected = false
    private lateinit var connectJob: Job

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()

        if (bluetoothAdapter == null) {
            Toast.makeText(this, "블루투스를 사용할 수 없습니다", Toast.LENGTH_LONG).show()
            finish()
            return
        }

        if (!bluetoothAdapter!!.isEnabled) {
            val enableBtIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT)
        } else {
            checkPermissionsAndConnect()
        }

        val button: Button = findViewById(R.id.button)
        button.setOnClickListener {
            if (isConnected) {
                sendCommand("DROP_BATTERY")
            } else {
                Toast.makeText(this, "블루투스가 연결되지 않았습니다", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun checkPermissionsAndConnect() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                    arrayOf(Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.ACCESS_COARSE_LOCATION,
                        Manifest.permission.BLUETOOTH_SCAN,
                        Manifest.permission.BLUETOOTH_CONNECT),
                    REQUEST_LOCATION_PERMISSIONS)
            } else {
                connectToDeviceInBackground()
            }
        } else {
            connectToDeviceInBackground()
        }
    }

    private fun connectToDeviceInBackground() {
        connectJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                val device: BluetoothDevice = bluetoothAdapter!!.getRemoteDevice(DEVICE_ADDRESS)
                bluetoothSocket = device.createRfcommSocketToServiceRecord(UUID_INSECURE)
                bluetoothSocket!!.connect()
                isConnected = true
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "장치에 연결되었습니다", Toast.LENGTH_SHORT).show()
                }
            } catch (e: IllegalArgumentException) {
                e.printStackTrace()
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "유효하지 않은 블루투스 주소입니다", Toast.LENGTH_SHORT).show()
                }
            } catch (e: IOException) {
                e.printStackTrace()
                isConnected = false
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "연결에 실패했습니다", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun sendCommand(input: String) {
        if (bluetoothSocket != null) {
            try {
                bluetoothSocket!!.outputStream.write(input.toByteArray())
            } catch (e: IOException) {
                e.printStackTrace()
                Toast.makeText(this, "명령 전송 중 오류가 발생했습니다", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_LOCATION_PERMISSIONS) {
            if ((grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED)) {
                connectToDeviceInBackground()
            } else {
                Toast.makeText(this, "블루투스 사용을 위해 위치 권한이 필요합니다", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_ENABLE_BT && resultCode == Activity.RESULT_OK) {
            checkPermissionsAndConnect()
        } else {
            Toast.makeText(this, "블루투스가 활성화되지 않았습니다", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::connectJob.isInitialized && connectJob.isActive) {
            connectJob.cancel()
        }
        bluetoothSocket?.close()
    }
}
